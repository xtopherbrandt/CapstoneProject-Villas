from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask import Flask
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)

db = SQLAlchemy()
ma = Marshmallow(app)

"""
setup_db(app)
    binds a flask application and a SQLAlchemy service
"""
def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config['DATABASE_URI']
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.app_context():
        db.init_app(app)    
        Migrate( app, db )
    
Base = declarative_base()