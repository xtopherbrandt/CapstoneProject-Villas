#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import os
import dateutil.parser
import babel
from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import logging
from logging import Formatter, FileHandler
from flask_migrate import Migrate
import config
import traceback

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
def create_app(test_config=False):
    app = Flask(__name__)
    config_app(app, test_config)
    
    return app

def config_app(app, test_config=False ):
#    print(f"config test={test_config}")
#    for line in traceback.format_stack():
#        print(line.strip())
    # create and configure the app
    moment = Moment(app)
    
    with app.app_context():
        if test_config:
            app.config.from_object(config.UnitTestConfig)
            db = setup_db(app)

        else:
            app.config.from_object(config.LocalConfig)
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

from models.modelBase import db

"""
setup_db(app)
    binds a flask application and a SQLAlchemy service
"""
def setup_db(app) -> SQLAlchemy:
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config['DATABASE_URI']
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)    
    db.create_all()
    Migrate( app, db )
    return db
    
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
