from flask import Flask, request,jsonify, abort
from models.user_model import User, UserSchema
from models.user_model import UserContact, UserContactSchema
from models.model_base import db
import requests
from marshmallow.exceptions import ValidationError
from marshmallow import EXCLUDE
from authlib.integrations.flask_oauth2 import ResourceProtector
from validator import Auth0JWTBearerTokenValidator, domain, audience
import json
import random, string
from sqlalchemy import select
from sqlalchemy.orm import join

app = Flask(__name__)

require_auth = ResourceProtector()
validator = Auth0JWTBearerTokenValidator(
    domain=domain,
    audience=audience
)
require_auth.register_token_validator(validator)

def validate_user(user) -> object:
    '''
    Determines if the user object meets the requirements
    
    If the user is not valid, the message in the return indicates why.
    
    return:
        {
            valid: bool
            message: string
        }
    '''
    response = {
        "valid" : False,
        "message" : "Unknown"
    }
    
    if user['first_name'] is None or len(user['first_name']) < 2 :
        response['message'] = 'first_name is required and must be at least 2 characters.'
        return response        
    
    if user['last_name'] is None or len(user['last_name']) < 2 :
        response['message'] = 'last_name is required and must be at least 2 characters.'
        return response        

    response['valid'] = True
    response['message'] = ''
    
    return response

def get_management_api_auth_token(app):
    '''
    Gets a machine to machine auth token from Auth0
    Client ID and Client Secret will be for the Test Application in Auth0 not the production application
    '''
    auth0_base_uri = f'https://{app.config["AUTH0_DOMAIN"]}'
    
    body={
        "client_id": app.config['AUTH0_BACKEND_CLIENT_ID'],
        "client_secret": app.config['AUTH0_BACKEND_CLIENT_SECRET'],
        "audience": app.config['AUTH0_MANAGEMENT_API_AUDIENCE'],
        "grant_type": 'client_credentials',
    }
    response = requests.post(f'{auth0_base_uri}/oauth/token', json=body, headers={'content-type': "application/json"})
    
    return response.json()['access_token']

def random_string(length):
   letters = string.printable
   return ''.join(random.choice(letters) for i in range(length))

def define_routes(app):
    
    @app.route('/user-invite', methods=['POST'])
    @require_auth('create:user')
    def invite_user():
        '''
        Invite User
            Triggers an invitation email to be sent from Auth0 to the e-mail address.
            The user is created in the Auth0 database, given the specified role and has the unit number saved in their meta-data
            The villa user is created to map to the Auth0 user
        Body: 
            {
                "email_address" : string : required
                "user_role" : string : villa-guest | villa-manager : required
                "unit_number" : integer : required
            }
        Response:
            {
                "success" : Boolean
                "user_id" : string
            }
            
        Status : 
            200 - User invitation sent
            409 - User already exists
        '''
        
        user_data = request.get_json()

        token = get_management_api_auth_token(app)      
        
        auth0_base_uri = f'https://{app.config["AUTH0_DOMAIN"]}'
        
        headers = {
            'Content-Type': "application/json",
            'Accept' : 'application/json',
            'Authorization' : f'Bearer {token}'
        }
        
        #check the role first to avoid creating a user with no role
        role_id = get_id_of_role(app, token, user_data['user_role'])
        
        if len(role_id) == 0 :
            abort(400, f'Invalid role: {user_data["user_role"]}')
        
        #now create the user in Auth0
        user_id = create_auth0_user( auth0_base_uri, headers, user_data['email_address'], user_data['unit_number'] )
        
        # Next assign the user to the role
        assign_user_to_role(auth0_base_uri, headers, user_id, role_id)

        # Now create a user in our database
        create_user(user_id)
        
        # Finally, send a password change e-mail to the new user
        # Auth0 needs to be configured with the login url for Villas so that the user can be redirected to Villas after changing their password
        send_change_password_email(auth0_base_uri, headers, app.config['AUTH0_CLIENT_ID'], user_data['email_address'])
        
        return jsonify({
            'success': True,
            'user_id': user_id
        })
    
    @app.route('/user', methods=['POST'])
    @require_auth('update:user')
    def post_user():
        '''
        Create User Profile
        Body: Valid User object:
            {
                "auth0_user_id" : string : required,
                "first_name" : string : required,
                "last_name" : string : required,
                "home_address_line_1" : string,
                "home_address_line_2" : string,
                "home_city" : string,
                "home_province" : string,
                "home_country" : string,
                "home_postal_code" : string,
                "phone_number" : string
            }
        Response:
            {
                "success" : Boolean,
                "user": User
            }
        '''            
        success = False

        user_data = request.get_json()
        
        if user_data == {}:
            print("User data was empty")
            abort(400, "User data was empty.")
        
        print(user_data)

        villa_user = User.query.filter_by(auth0_id = user_data['auth0_user_id']).one_or_none()

        if villa_user is None:
            message = f'No user found with auth0_user_id = {user_data["auth0_user_id"]}'
            abort(404, message)        

        try:
            user_schema = UserContactSchema(unknown=EXCLUDE)
            posted_user_contact = user_schema.load(user_data)
            posted_user_contact.set_user_id( villa_user.get_id() )
            
        except ValidationError as e:
            print(e.messages)
            abort(400, e.messages)
                    
        print(posted_user_contact)
        try:
            db.session.add(posted_user_contact)
            db.session.commit()
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)
            abort(500)                

        success = True

        print(f'user: {user_schema.dump(posted_user_contact)}')
        return jsonify({
            'success': success,
            'user': user_schema.dump(posted_user_contact)
        })
        
    @app.route('/user/<string:auth0_user_id>', methods=['GET'])
    @require_auth('read:user')
    def get_user_contact(auth0_user_id):
        '''
        Get User Contact

        Route: /user/<auth0_user_id>
        Method: GET
        Response:
            {
                "success" : Boolean,
                "user": User
            }
        '''
        
        success = False
        statement = select(User, UserContact).join(UserContact, isouter=True).where(User.auth0_id == auth0_user_id)
        session = db.session
        
        print( f'Get user contact: {auth0_user_id}')
        try:
            results = session.execute(statement).fetchone()
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)
            abort(500)
        if results is None:
            message =  f'A user with Auth0 user id:{auth0_user_id} was not found in the villas database'
            abort(404, message)         
         
        # results is a complex type of Row[Tuple[User, UserContact]]
        # need to get the User object out to load into the schema
        user_schema = UserSchema().dumps(results[0])
 
        success = True

        return jsonify({
            'success': success,
            'user': user_schema
        })        
        
def get_id_of_role(app, token, role_name) -> string:
    
    role_list = get_roles(app, token)
    
    for role in role_list:
        if role['name'] == role_name :
            return role['id']
    
    return ''
    
def get_roles(app, token) -> []:

    url = f'https://{app.config["AUTH0_DOMAIN"]}/api/v2/roles'
    
    payload = {}
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.json()

def create_auth0_user(auth0_base_uri, headers, email_address, unit_number) -> string:
    
    create_user_endpoint = '/api/v2/users'
    auth0_database_connection_name = 'Username-Password-Authentication'
    
    body = {
        "email": email_address,
        "password" : random_string(20),
        "user_metadata": { 'unit_number' : unit_number },
        "connection": auth0_database_connection_name           
    }
    
    response = requests.post(f'{auth0_base_uri}{create_user_endpoint}', json=body, headers=headers)
    
    if response.status_code == 409 : #user already exists
        abort(409, "User already exists.")
    elif response.status_code != 201 :
        message = f'Auth0 create user API responded with {response.status_code}'
        print( message )
        abort(500, message)
    
    if 'user_id' in response.json():
        user_id = response.json()['user_id']
    else:
        message = 'Auth0 did not provide a user_id in the response to create user'
        print( message )
        abort( 500, message )

    return user_id
    
def assign_user_to_role(auth0_base_uri, headers, user_id, role_id):
    
    assign_to_role_endpoint = f'/api/v2/roles/{role_id}/users'

    body = {
        "users" : [f'{user_id}']
    }        

    response = requests.post(f'{auth0_base_uri}{assign_to_role_endpoint}', json=body, headers=headers)

    if response.status_code != 200 :
        message = f'Auth0 assign user to role API responded with {response.status_code}'
        print( message )
        abort(500, message)
        
                
def create_user(auth0_user_id) -> User :
    if auth0_user_id is None: abort(500, 'Need a valid Auth0 User Id to create a user')
    
    user = User(auth0_id = auth0_user_id)
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        if hasattr(e, 'message'):
            print(e.message)
        else:
            print(e)
        abort(500)                
    
    return user

def send_change_password_email(auth0_base_uri, headers, client_id, email_address):
    
    password_change_endpoint = f'/dbconnections/change_password'
    body = {
        "email": email_address,
        "client_id": client_id,
        "connection": "Username-Password-Authentication"
    }   

    response = requests.post(f'{auth0_base_uri}{password_change_endpoint}', json=body, headers=headers)
    
    if response.status_code != 200:
        message = f'Auth0 change password trigger responded with {response.status_code}'
        print( message )
        abort(500, message)          