from flask import Flask, request,jsonify, abort
from models.user_model import User, UserSchema
from models.model_base import db
import requests
from marshmallow.exceptions import ValidationError
from authlib.integrations.flask_oauth2 import ResourceProtector
from validator import Auth0JWTBearerTokenValidator, domain, audience
import json
import random, string

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
        Body: 
            {
                "email_address" : string : required
                "user_role" : string : villa-guest | villa-manager : required
                "unit_number" : integer : required
            }
        Response:
            {
                "success" : Boolean
            }
            
        Status : 
            200 - User invitation sent
            409 - User already exists
        '''
        success = False
        
        user_data = request.get_json()

        token = get_management_api_auth_token(app)      
        
        auth0_base_uri = f'https://{app.config["AUTH0_DOMAIN"]}'
        
        #check the role first to avoid creating a user with no role
        role_id = get_id_of_role(app, token, user_data['user_role'])
        
        if len(role_id) == 0 :
            abort(400, f'Invalid role: {user_data["user_role"]}')
        
        #now create the user in Auth0
        create_user_endpoint = '/api/v2/users'
        auth0_database_connection_name = 'Username-Password-Authentication'
        
        headers = {
            'Content-Type': "application/json",
            'Accept' : 'application/json',
            'Authorization' : f'Bearer {token}'
        }
        body = {
            "email": user_data['email_address'],
            "password" : random_string(20),
            "user_metadata": { 'unit_number' : user_data['unit_number'] },
            "connection": auth0_database_connection_name           
        }
        
        response = requests.post(f'{auth0_base_uri}{create_user_endpoint}', json=body, headers=headers)
        
        if response.status_code == 201 :
            success = True
        elif response.status_code == 409 : #user already exists
            abort(409, "User already exists.")
        else :
            message = f'Auth0 create user API responded with {response.status_code}'
            print( message )
            abort(500, message)
        
        if 'user_id' in response.json():
            user_id = response.json()['user_id']
        else:
            abort(500, 'Auth0 did not provide a user_id in the response to create user')
        
        # Next assign the user to the role
        assign_to_role_endpoint = f'/api/v2/roles/{role_id}/users'

        body = {
            "users" : [f'{user_id}']
        }        

        response = requests.post(f'{auth0_base_uri}{assign_to_role_endpoint}', json=body, headers=headers)

        if response.status_code == 200 :
            success = True
        else :
            message = f'Auth0 assign user to role API responded with {response.status_code}'
            print( message )
            abort(500, message)

        # Finally, send a password change e-mail to the new user
        # Auth0 needs to be configured with the login url for Villas so that the user can be redirected to Villas after changing their password
        password_change_endpoint = f'/dbconnections/change_password'
        body = {
            "email": user_data['email_address'],
            "client_id": app.config['AUTH0_CLIENT_ID'],
            "connection": "Username-Password-Authentication"
        }   

        response = requests.post(f'{auth0_base_uri}{password_change_endpoint}', json=body, headers=headers)
        
        print(response.text)
        
        return jsonify({
            'success': success,
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
            abort(400, "User data was empty.")
        
        print(user_data)
            
        try:
            user_schema = UserSchema()
            user = user_schema.load(user_data)
        except ValidationError as e:
            print(e.messages)
            abort(400, e.messages)
                    
        print(user)
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)
            abort(500)                

        success = True

        print(user_schema.dump(user))
        return jsonify({
            'success': success,
            'user': user_schema.dump(user)
        })
        
    @app.route('/user/<int:user_id>', methods=['GET'])
    @require_auth('read:user')
    def get_user(user_id):
        '''
        Get User

        Route: /user/<id>
        Method: GET
        Response:
            {
                "success" : Boolean,
                "user": User
            }
        '''
        
        success = False
        print( f'Get user: {user_id}')
        try:
            user = User.query.filter(User.id == user_id).one_or_none()
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)
            abort(500)
        if user is None:
            abort(404)            
        user_schema = UserSchema()
        user_deserialized = user_schema.dump(user)
        
        print(user)
 
        success = True

        print(user_schema.dump(user))
        return jsonify({
            'success': success,
            'user': user_deserialized
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
