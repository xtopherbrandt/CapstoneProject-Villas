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
    
    configuration_file_name = os.environ.get('CONFIG_FILE_NAME', default='env_local.json')
    print (f"Using config file: {configuration_file_name}. Set $env:CONFIG_FILE_NAME to load a different configuration.")

    config_app(app, configuration_file_name)
    define_routes(app)
    define_error_handlers(app)
    print(list_routes(app))
    return app

def config_app(app, configuration_file_name ):

    moment = Moment(app)
    
    with app.app_context():
        app.config.from_file(configuration_file_name, load=json.load)
        DATABASE_URI = "postgresql://{}:{}@{}/{}".format(
            app.config['DB_USERNAME'],
            app.config['DB_PASSWORD'],
            app.config['DB_HOST'],
            app.config['DB_NAME']
        )
        app.config['DATABASE_URI'] = DATABASE_URI
        
    setup_db(app)
    CORS(app)
        
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
