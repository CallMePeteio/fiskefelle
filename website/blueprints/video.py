
from flask_login import login_required
from flask_login import current_user

from flask import send_from_directory
from flask import render_template
from flask import current_app
from flask import Blueprint
from flask import Response
from flask import session
from flask import request
from flask import jsonify

from ..services.dbService import selectFromDB
from ..services.rtsp import getDirSize
from ..models import Videos

from .. import logging
from .. import config 
from .. import app
from .. import db

import threading 
import datetime
import sqlite3
import time
import json
import cv2
import os 


video = Blueprint('video', __name__) # MAKES THE BLUPRINT OBJECT


@video.route("/video", methods=["POST","GET"])
@login_required
def videoTable():


    if request.method == "POST":
        if request.form.get("downloadVideoId"):
            pass

        if request.form.get("deleteVideoId"):
            videoName = request.form.get("deleteVideoName") # GETS THE VIDEO NAME
            recordingDir = os.path.abspath(config.recordingsFolder) # GETS THE FULL RECORDING PATH
            recordingsFile = os.path.join(recordingDir, videoName + ".avi") # ADDS THE VIDEO NAME TO THE RECORDING PATH

            if os.path.exists(recordingsFile): # CHECKS IF THE FILE EXISTS
                os.remove(recordingsFile) # DELETES THE FILE
            else:
                logging.critical(f"     Couldn't find the specified avi file to delete: {recordingsFile}")

            video_id = request.form.get("deleteVideoId")
            video = Videos.query.get(video_id) # get the Video object using the id
            if video:
                db.session.delete(video) # delete the Video object
                db.session.commit() # commit the transaction
  



    videoItems = selectFromDB(dbPath=config.pathToDB, table="videos") # GETS ALL OF THE DATA FROM THE TABLE "videos"
    return render_template("video.html", videoItems=videoItems, user=current_user, isAdmin=session.get("isAdmin", False))


@video.route("/rtspStream", methods=["POST","GET"])      
def generateRstpPaths():
    if app.stream != None:

        while app.stream.isReadingFrames == False: # WHILE THE RTSP LINK IS GETTING SETUP
            return render_template("loading.html")

        while True:
            return Response(app.stream.generateVideo(),mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return render_template("error/rtspError.html")



@video.route("/test", methods=["POST","GET"])      
def test():
    return render_template("loading.html")




