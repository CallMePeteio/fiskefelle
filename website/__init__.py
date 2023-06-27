

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_caching import Cache
from flask import Flask

from .services.relay import switchFan
from .services.relay import Relay

from . import config

import threading
import datetime
import sqlite3
import logging  
import smbus
import numpy
import json
import time
import sys
import cv2
import os




global cache
cache = None

db = SQLAlchemy()


from .services.loggingFont import formatFont
logger = logging.getLogger() # MAKES THE LOGGING OBJECT
logger.setLevel(config.loggingLevel) # SETS THE LEVEL AS DEFINED ABOVE
logger = formatFont(logger)



#relay = Relay(i2cAdress=0x20, initialState=[0,0,0,0,0,0]) # MAKES THE RELAY OBJECT, FOR CONTROLLING THE RELAY HAT
#threading.Thread(target=switchFan, args=(2, 50, 75, 5)).start()




"""
___________________________________ create_app ___________________________________
This function creates a Flask application with several configurations including a secret key and a database connection.

Inputs:
None.

Returns:
The function returns a Flask application instance.
"""
def create_app():
    global stream
    global cache
    global app

    app = Flask(__name__) # Creates an instance of Flask application with the given name
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs' # Sets the secret key used for signing session cookies
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{config.dbName}' # Sets the URI of the SQLite database
    app.config['CACHE_TYPE'] = 'simple'  # You can also use 'redis', 'memcached', or other cache types

    db.init_app(app) # Initializes the SQLAlchemy database instance with the Flask app instance

    cache = Cache(app)

    from .blueprints.settings import settings
    from .blueprints.video import video
    from .blueprints.home import home
    from .blueprints.auth import auth

    from .blueprints.api import api


    app.register_blueprint(api, url_prefix='/') # Registers the auth blueprint with the Flask app instance
    app.register_blueprint(home, url_prefix='/') # Registers the views blueprint with the Flask app instance
    app.register_blueprint(settings, url_prefix='/') # Registers the views blueprint with the Flask app instance
    app.register_blueprint(auth, url_prefix='/') # Registers the auth blueprint with the Flask app instance
    app.register_blueprint(video, url_prefix='/') # Registers the auth blueprint with the Flask app instance

    from .models import User, Log

    with app.app_context():
        db.create_all() # Creates all tables specified in the models

    login_manager = LoginManager() # Initializes the LoginManager instance
    login_manager.login_view = 'auth.login' # Sets the name of the login view
    login_manager.init_app(app) # Initializes the LoginManager instance with the Flask app instance

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id)) # Defines a callback function to load a user from the database

    from .services.rtsp import startRtspStream
    app.stream = startRtspStream(db, app, logging, config.rtspLink, config.resolution, config.framesPerSecond, config.userId_, config.recordingsFolder)

    return app # Returns the Flask app instance





"""
___________________________________ create_database ___________________________________
This function creates a database if it does not exist.

"""
def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app) # Creates all tables in the database
        print('Created Database!') # Prints a message indicating that the database has been created.



