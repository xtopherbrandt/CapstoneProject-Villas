from flask import Flask, request,jsonify, abort
from models.user_model import User, UserSchema
from models.model_base import db

from marshmallow.exceptions import ValidationError
from authlib.integrations.flask_oauth2 import ResourceProtector
from validator import Auth0JWTBearerTokenValidator, domain, audience
import json

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

def define_routes(app):
    
    @app.route('/user', methods=['POST'])
    @require_auth('create:user')
    def post_user():
        '''
        Create User
        Body: Valid User object:
            {
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
        print( f'POST /user: {user_data}' )
        
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