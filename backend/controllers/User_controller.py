from flask import Flask, request,jsonify, abort
from models.user_model import User, UserSchema
from models.model_base import db

from marshmallow.exceptions import ValidationError

app = Flask(__name__)

        

def define_routes(app):
    
    '''
    Create User

    Route: /user
    Method: POST
    Body: Valid User object:
        {
            "first_name" : string,
            "last_name" : string,
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
    @app.route('/user', methods=['POST'])
    def post_user():
        success = False
        
        user_data = request.get_json()
        
        if user_data == {}:
            abort(400)
            
        print(user_data)
        
        try:
            user_schema = UserSchema()
            user = user_schema.load(user_data)
        except ValidationError as e:
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
    @app.route('/user/<int:user_id>', methods=['GET'])
    def get_user(user_id):
        success = False
        
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