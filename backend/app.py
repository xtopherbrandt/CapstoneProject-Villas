#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import os
import dateutil.parser
import babel
from flask import Flask
from flask_moment import Moment
from flask_cors import CORS

import logging
from logging import Formatter, FileHandler
from models.model_base import setup_db
import traceback
import os
import json
from controllers.User_controller import define_routes
from error_handling import define_error_handlers

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
def create_app():
    app = Flask(__name__)
    
    USE_POD_ENV_CONFIG = os.environ.get('USE_POD_ENV_CONFIG', default=False)
    if USE_POD_ENV_CONFIG :
        print ('Loading config from environment variables')
        load_config_from_env(app)
    else :
        configuration_file_name = os.environ.get('CONFIG_FILE_NAME', default='env_local.json')
        print (f"Using config file: {configuration_file_name}. Set $env:CONFIG_FILE_NAME to load a different configuration.")
        load_config_from_file(app, configuration_file_name)
        
    config_app(app)
    define_routes(app)
    define_error_handlers(app)
    print(list_routes(app))
    return app

def load_config_from_file(app, configuration_file_name):
    app.config.from_file(configuration_file_name, load=json.load)

def load_config_from_env(app):
    app.config['DB_USERNAME'] = os.environ.get('DB_USERNAME')
    app.config['DB_PASSWORD'] = os.environ.get('DB_PASSWORD')
    app.config['DB_HOST'] = os.environ.get('DB_HOST')
    app.config['DB_NAME'] = os.environ.get('DB_NAME')
    
def config_app(app):

    moment = Moment(app)
    
    with app.app_context():
        DATABASE_URI = "postgresql://{}:{}@{}/{}".format(
            app.config['DB_USERNAME'],
            app.config['DB_PASSWORD'],
            app.config['DB_HOST'],
            app.config['DB_NAME']
        )
        app.config['DATABASE_URI'] = DATABASE_URI
        print(f'Database URI: {DATABASE_URI}')
        
    setup_db(app)
    
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        response.headers.add(
            "Access-Control-Allow-Credentials", "true"
        )
        return response
            
    app.jinja_env.filters['datetime'] = format_datetime

    if not app.debug:
        file_handler = FileHandler('error.log')
        file_handler.setFormatter(
            Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        )
        app.logger.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.info('errors')


def list_routes(app):
    return ['%s' % rule for rule in app.url_map.iter_rules()]

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')


#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#
