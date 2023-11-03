from models.model_base import ma, Base, db
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from marshmallow import post_load, Schema, fields
from marshmallow.validate import Length

#these imports are required to allow Marshmallow to follow links
from models.province_state_model import ProvinceState
from models.country_model import Country


class UserContact(db.Model):
    __tablename__ = 'villa_user_contact'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("villa_user.id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates='user_contact')
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(13), nullable=False)
    home_address_line_1: Mapped[str] = mapped_column(String(100), nullable=False)
    home_address_line_2: Mapped[str] = mapped_column(String(100), nullable=True)
    home_city: Mapped[str] = mapped_column(String(100), nullable=False)
    home_province: Mapped[str] = mapped_column(ForeignKey("province_state.id"), nullable=False)
    home_country: Mapped[str] = mapped_column(ForeignKey("country.id"), nullable=False)
    home_postal_code: Mapped[str] = mapped_column(String(6), nullable=False)
    
    def set_user_id(self, value):
        if type(value) == int:
            self.user_id = value
            
    def __repr__(self):
        return f'<User Contact {self.id} \n \
                    user_id: {self.user_id} \n \
                    first_name: {self.first_name} \n \
                    last_name: {self.last_name} \n \
                    home_address_line_1: {self.home_address_line_1} \n \
                    home_address_line_2: {self.home_address_line_2} \n \
                    home_city: {self.home_city} \n \
                    home_province: {self.home_province} \n \
                    home_country: {self.home_country} \n \
                    home_postal_code: {self.home_postal_code} \n \
                    phone_number: {self.phone_number} >'    


class UserContactSchema(Schema):

    id = fields.Integer()
    user_id = fields.Integer()
    first_name = fields.String(required=True, validate=Length(min=2, error='first_name must be at least 2 characters'), error_messages={"required":"first_name is required."})
    last_name = fields.String(required=True, validate=Length(min=2, error='last_name must be at least 2 characters'), error_messages={"required":"last_name is required."})
    phone_number = fields.String(required=True)
    home_address_line_1 = fields.String(required=True)
    home_address_line_2 = fields.String(required=False)
    home_city = fields.String(required=True)
    home_province = fields.String(required=True)
    home_country = fields.String(required=True)
    home_postal_code = fields.String(required=True)
        
    @post_load
    def make_user_contact(self, data, **kwargs):
        return UserContact(**data)