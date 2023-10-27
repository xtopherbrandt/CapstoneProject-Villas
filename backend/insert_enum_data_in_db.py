from models.country_enum import Country as Country_enum
from models.province_state_enum import Provinces_States as Province_States_enum
from models.country_model import Country
from models.province_state_model import ProvinceState
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import json
import os
    
def populate_enums():
    
    USE_POD_ENV_CONFIG = os.environ.get('USE_POD_ENV_CONFIG', default=False)
    if USE_POD_ENV_CONFIG :
        print ('Loading config from environment variables')
        database_uri = "postgresql://{}:{}@{}/{}".format(
            os.environ.get('DB_USERNAME'),
            os.environ.get('DB_PASSWORD'),
            os.environ.get('DB_HOST'),
            os.environ.get('DB_NAME')
        )

    else :
        config_file = open('env_local.json')
        config = json.load(config_file)
        database_uri = "postgresql://{}:{}@{}/{}".format(
            config['DB_USERNAME'],
            config['DB_PASSWORD'],
            config['DB_HOST'],
            config['DB_NAME']
        )
            
    print(database_uri)
    engine = create_engine(database_uri)
    
    with Session(engine) as session:
        for country in Country_enum:
            print(country)
            entry = Country(id = country.name, name = country.value)        
            session.add(entry)
        
        for province in Province_States_enum:
            print(province.name)
            entry = ProvinceState(id = province.name)
            session.add(entry)
            
        session.commit()
    
populate_enums()