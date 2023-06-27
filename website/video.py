
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


from .physical.rtsp import readRecStartVar
from .models import Videos

from . import maxRecordSizeGB
from . import selectFromDB
from . import getDirSize    
from . import pathToDB
from . import logging
from . import app
from . import db

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
            recordingDir = os.path.abspath("website/recordings") # GETS THE FULL RECORDING PATH
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
  



    videoItems = selectFromDB(dbPath=pathToDB, table="videos") # GETS ALL OF THE DATA FROM THE TABLE "videos"
    return render_template("video.html", videoItems=videoItems, user=current_user, isAdmin=session.get("isAdmin", False), is_recording=readRecStartVar())


@video.route("/rtspStream", methods=["POST","GET"])      
def generateRstpPaths():

    # NOTE NEEED TO FIGURE OUT A WAY FOR ONLY AUTHORIZED USERS TO VIEW THE STREAM 
    from . import stream

    rtspLink = "rtsp://admin:Troll2014@192.168.1.20:554"
    selectedCamera = selectFromDB(dbPath=pathToDB, table="camera", argumentList=["WHERE"], columnList=["ipAdress"], valueList=[rtspLink])

    while True:
        if selectedCamera[0][3] == True: # CHECKS IF THE RSTP COLUMN IS TRUE
            return Response(stream.generateVideo(),mimetype='multipart/x-mixed-replace; boundary=frame')


@video.route("video/download/<name>")
def downloadVideo(name):
    recordings_dir = os.path.abspath("website/recordings")
    return send_from_directory(recordings_dir, name + ".avi", as_attachment=True)


@video.route("/usedVidSpace", methods=["GET"])
@login_required
def getUsedVidSpace():
    recDir = os.path.abspath("website/recordings") # FINDS THE FULL PATH TO THE RECORDING DIR
    recDirSize = getDirSize(recDir)

    return jsonify({"usedSpace": recDirSize, "maxSpace": maxRecordSizeGB})



