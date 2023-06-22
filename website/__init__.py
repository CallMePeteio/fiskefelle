

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_caching import Cache
from flask import Flask

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


def convertSecToHMS(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
def readRecStartVar():
    instanceDir = os.path.abspath("instance") # GETS THE FULL PATH OF THE INSTANCE DIRECTORY
    recJsonPath = instanceDir + "/startRecord.json" # MAKES THE FULL PATH TO THE JOSN FILE


    try: 
        with open(recJsonPath) as f:
            data = json.load(f)
    except:
        return None

    return  data["startRec"]

class RtspStream():
    def __init__(self, rtspLink, res, fps, userId):
        
        self.rtspLink = rtspLink
        self.res = res
        self.fps = fps

        self.userId = userId
        self.frame = None

        self.camera=cv2.VideoCapture(rtspLink)

    def readFrame(self): 
        while True:
            success = False
            while success == False:
                success, self.frame = self.camera.read()


    def recordVideo(self):
        while True: 
            time.sleep(1)
            if readRecStartVar() == True:
                currentTime = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S") # GETS THE CUREENT TIME IN (DAY,MONTH,YEAR HOUR-MINUTE-SECOND) FORMAT
                name = str(currentTime) # CONVERTS THE DATETIME OBJECT TO A STRING, FOR NAME USAGE

                recDir = os.path.abspath("website/recordings") # FINDS THE FULL PATH TO THE RECORDING DIR
                recPath = os.path.join(recDir, name + ".avi") # APPENDS THE FILE NAME + THE .avi EXTENTION

                writer = cv2.VideoWriter(recPath, cv2.VideoWriter_fourcc(*'XVID'), self.fps, self.res) # MAKES THE VIDEOWRITER OBJECT
                startTime = time.time() # SETS TGE START TIME, TO CALCULATE THE TOTAL LENGTH OF THE VIDEO

                logging.info("      Started recording!")
                print(f"recordVideo called in thread {threading.get_ident()}")

                prevFrame = self.frame
                while readRecStartVar() == True or readRecStartVar() == None and int(time.time() - startTime) < 3600 * 2:
                    if not numpy.array_equal(self.frame, prevFrame):
                        prevFrame = self.frame
                        writer.write(self.frame) # WRITES THE FRAME TO THE VIDEOWRITER OBJECT NOTE THE INPUT FPS MUST MATCH THE FPS OF THE CAMERA TO GET CORRECT LENGTH

                with app.app_context(): # OPENS WITH APP CONTEXT TO ALLOW TO WRITE TO THE DB¨
                    from .models import Videos
                    elapsedTime = convertSecToHMS(int(time.time() - startTime)) # GETS THE ELAPSED TIME AND RETURNS A STRING IN (hr:min:sec) FORMAT
                    video_ = Videos(userId=self.userId, fileName=name, duration=elapsedTime) # ADDS THE VIDEO INTO THE DB
                    db.session.add(video_)
                    db.session.commit()   

                    writer.release() # CLOSES THE WRITER OBJECT (makes a new one when the user wants to record another video)
                    logging.info("      Stopped recording!") 


    def generateVideo(self):
        prevFrame = self.frame

        while True: 
            if not numpy.array_equal(self.frame, prevFrame):
                prevFrame = self.frame
                ret, buffer = cv2.imencode(".jpg", self.frame)
                byteArr=buffer.tobytes() # CONVERTS THE FRAME TO A BYTEARRAY

                yield(b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + byteArr + b'\r\n')


global cache
cache = None

db = SQLAlchemy()
DB_NAME = "database.db"
pathToDataStorage = "/home/pi/fiskefelle/instance/"
pathToDB = pathToDataStorage + DB_NAME


"""
Level: NOTSET > DEBUG > INFO > WARNING > ERROR > CRITICAL
Value:   0    >  10   >  20  >    30   >  40   >  50
"""
from .loggingFont import formatFont
loggingLevel = 20 # DEFINES THE LOGGING LEVEL
logger = logging.getLogger() # MAKES THE LOGGING OBJECT
logger.setLevel(loggingLevel) # SETS THE LEVEL AS DEFINED ABOVE
logger = formatFont(logger)


rtspLink = "rtsp://root:Troll2014!@192.168.1.21/axis-media/media.amp"
stream = RtspStream(rtspLink, (1280, 720),  15,  1)
threading.Thread(target=stream.readFrame, args=()).start()
time.sleep(0.5)
threading.Thread(target=stream.recordVideo, args=()).start()




"""
___________________________________ create_app ___________________________________
This function creates a Flask application with several configurations including a secret key and a database connection.

Inputs:
None.

Returns:
The function returns a Flask application instance.
"""
def create_app():
    global cache
    global app

    app = Flask(__name__) # Creates an instance of Flask application with the given name
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs' # Sets the secret key used for signing session cookies
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}' # Sets the URI of the SQLite database
    app.config['CACHE_TYPE'] = 'simple'  # You can also use 'redis', 'memcached', or other cache types

    db.init_app(app) # Initializes the SQLAlchemy database instance with the Flask app instance

    cache = Cache(app)

    from .backEnd import backEnd
    from .views import views
    from .auth import auth
    from .video import video

    app.register_blueprint(backEnd, url_prefix='/') # Registers the auth blueprint with the Flask app instance
    app.register_blueprint(views, url_prefix='/') # Registers the views blueprint with the Flask app instance
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

    return app # Returns the Flask app instance






"""
___________________________________ create_database ___________________________________
This function creates a database if it does not exist.

Inputs:
app: A Flask app instance.

Returns:
None.
"""
def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app) # Creates all tables in the database
        print('Created Database!') # Prints a message indicating that the database has been created.










"""
___________________________________________ selectFromDB _________________________________________
This function reads data from a sqlite databace, it is dynamic in the sens that you could add an unlimteted parameters and unlimeded values to fit those parameters
The sqlite3 command is strored in the variable "getString"
dbPath = This is the path to the databace you want to read data from. example: "F:\Scripts\Python\canSat\website\instance\database.db" (str)
table = This is the name of the table you want to read data from. example: "flightmaster" (str)
columnList = This is the list of parameters you want to add to the "getString" variable. for example if you want to get data from column "id" then input ["id"]. If you want to inpuut and AND statment then add it in the lsit. For example if you want from the column id  where the loginId = 1 then input: ["id", "loginId"]. The value will be added under
valueList = This is the list of values you add to the column list.
argument = This is the argument you want to do, forexample could you add AND.
"""

def selectFromDB(dbPath, table, argumentList=None, columnList=None, valueList=None, log=True):
    def checkIfEmpty(data): 
        if data == []:
            return None
        return data
      
    con = sqlite3.connect(dbPath) # CONNECTS TO THE DB
    cursor = con.cursor() # MAKES THE CURSOR, FOR SELECTING THE DATA
    if argumentList != None and columnList != None and valueList != None: 

        getString = f"SELECT * FROM '{table}' {argumentList[0]} {columnList[0]}=?" # THIS IS THE STRING THAT IS GOING TO BE THE SQLITE COMMAND, ALREADY ADDED THE FIRST DATAPOINT
        if len(columnList) == len(valueList) or len(columnList) == 0 or len(valueList) == 0: # CHECKS IF THERE IS AN ERROR ON THE LENGTH OF THE INPUT PARAMETERS
            if len(columnList) >= 1: # IF THE INPUT PARAMETERS IS MORE THAN ONE, THEN IT ADDS THE AND SYNTAX AND THE PARAMETER TO THE GETSTRING VARIABLE
                for i, parameter in enumerate(columnList[1:]): # LOOPS OVER ALL OF THE EXTRA "AND" PARAMETERS
                    getString += f"{argumentList[i+1]} {parameter}=?"



                cursor.execute(getString, (valueList)) # SELECTS ALL OF THE DATA ACCORDING TO THE PARAMETERS GIVEN ABOVE
                data = cursor.fetchall() # FETCHES ALL OF THE DATA

                if log == True: # IF THE RESULTS SHULD BE LOGGED
                    logging.info(f"     Readed data from databace, command: {getString}{valueList}") # LOGS THE DATA
                    logging.debug(f"    data recived: {data}")

                return checkIfEmpty(data) # RETURNS ALL OF THE DATA


            cursor.execute(getString, (valueList[0],)) # SELECTS ALL OF THE GPS DATA, WE DO THIS TWICE BECAUSE THE SYNTAX OF THIS SUCS ;(, I NEED TI HAVE TRHE COMMA THERE WHAT A SHIT LIBARY
            data = cursor.fetchall() # FETCHES ALL OF THE DATA, GIVEN THE PARAMETERS ABOVE

            if log == True: # IF THE RESULTS SHULD BE LOGGED
                logging.info(f"     Databace command (read): {getString}{valueList}") # LOGS THE DATA
                logging.debug(f"    data recived: {data}")

            return checkIfEmpty(data) # RETURNS ALL OF THE DATA

        else: 
          raise Exception(f"Parameter error when reading from DB, there has to be a value for eatch parameter. Parameters: {columnList}, Values: {valueList}") # IF THERE WAS A ERROR OF THE LENGHT OF THE DATA
    else: 
        getString = f"SELECT * FROM '{table}'" # THIS IS THE STRING THAT IS GOING TO BE THE SQLITE COMMAND, ALREADY ADDED THE FIRST DATAPOINT
        cursor.execute(getString) # SELECTS ALL OF THE DATA ACCORDING TO THE PARAMETERS GIVEN ABOVE
        data = cursor.fetchall() # FETCHES ALL OF THE DATA

        if log == True: # IF THE RESULTS SHULD BE LOGGED
            logging.info(f"     Readed data from databace, command: {getString}{valueList}") # LOGS THE DATA
            logging.debug(f"    data recived: {data}")

        return checkIfEmpty(data)





def getNameAndAdminCamera(cameraTable): 

    rtnList = []
    if cameraTable != False and cameraTable != None:
        for row in cameraTable:
            rtnList.append((row[2], row[4]))
        return [rtnList, len(rtnList)] # returns the list and if admin can watch it: [('Trollfjrord', 1), ('Bælevåg', 0), ('Bodø', 1), ('Bodø', 0), ('Breivika', 0), ('Stavanger', 0)], only admin can view "Trollfjrord" and "Bodø"
    
    else:
        return False

