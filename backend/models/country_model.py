from sqlalchemy.orm import mapped_column
from sqlalchemy import String
from models.model_base import Base, ma, db

class Country(db.Model):
    __tablename__ = 'country'
    id = mapped_column(String(3), primary_key=True)
    name = mapped_column(String(100), nullable=False)
    
    def __repr__(self):
        return f'<Country {self.id} \n \
                    name: {self.name} >'
                    
class CountrySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Country
