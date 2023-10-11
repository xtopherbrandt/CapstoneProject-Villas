from models.model_base import ma, Base, db
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from marshmallow import post_load

#these imports are required to allow Marshmallow to follow links
from models.province_state_model import ProvinceState
from models.country_model import Country


class User(db.Model):
    __tablename__ = 'villa_user'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(13), nullable=True)
    home_address_line_1: Mapped[str] = mapped_column(String(100), nullable=True)
    home_address_line_2: Mapped[str] = mapped_column(String(100), nullable=True)
    home_city: Mapped[str] = mapped_column(String(100), nullable=True)
    home_province: Mapped[str] = mapped_column(ForeignKey("province_state.id"), nullable=True)
    home_country: Mapped[str] = mapped_column(ForeignKey("country.id"), nullable=True)
    home_postal_code: Mapped[str] = mapped_column(String(6), nullable=True)
    
    def __repr__(self):
        return f'<User {self.id} \n \
                    first_name: {self.first_name} \n \
                    last_name: {self.last_name} \n \
                    home_address_line_1: {self.home_address_line_1} \n \
                    home_address_line_2: {self.home_address_line_2} \n \
                    home_city: {self.home_city} \n \
                    home_province: {self.home_province} \n \
                    home_country: {self.home_country} \n \
                    home_postal_code: {self.home_postal_code} \n \
                    phone_number: {self.phone_number} >'    

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = True
    
    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)