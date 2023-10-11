from sqlalchemy.orm import mapped_column
from sqlalchemy import String
from models.model_base import Base, ma, db

class ProvinceState(db.Model):
    __tablename__ = 'province_state'
    id = mapped_column(String(2), primary_key=True)
    
    def __repr__(self):
        return f'<ProvinceState {self.id} >'
    
class ProvinceStateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProvinceState
