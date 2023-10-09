import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

class LocalConfig():
    
    DATABASE_URI = "postgresql://{}:{}@{}/{}".format(
        os.environ.get('DB_USERNAME_LOCAL'),
        os.environ.get('DB_PASSWORD_LOCAL'), 
        os.environ.get('DB_HOST_LOCAL'),
        os.environ.get('DB_NAME_LOCAL')
    )
    
class UnitTestConfig():

    DATABASE_URI = "postgresql://{}:{}@{}/{}".format(
        os.environ.get('DB_USERNAME_UNIT_TEST'),
        os.environ.get('DB_PASSWORD_UNIT_TEST'), 
        os.environ.get('DB_HOST_UNIT_TEST'),
        os.environ.get('DB_NAME_UNIT_TEST')
    )

