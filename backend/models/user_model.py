from models.model_base import ma, Base, db
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from marshmallow import post_load, Schema, fields
from marshmallow.validate import Length

'''
Maps the Villa User to an Auth0 User
'''

class User(db.Model):
    __tablename__ = 'villa_user'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    auth0_id: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    
    def __repr__(self):
        return f'<User {self.id} \n \
                    auth0_id: {self.auth0_id} >'    


class UserSchema(Schema):

    id = fields.Integer()
    auth0_id = fields.String(required=True)

        
    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)