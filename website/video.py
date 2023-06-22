
from flask_login import login_required
from flask_login import current_user

from flask import send_from_directory
from flask import render_template
from flask import Blueprint
from flask import Response
from flask import session
from flask import request
from flask import jsonify


from .models import Videos

from . import selectFromDB
from . import pathToDB
from . import logging
from . import stream
from . import app
from . import db

import subprocess
import threading 
import datetime
import sqlite3
import time
import json
import cv2
import os 


video = Blueprint('video', __name__) # MAKES THE BLUPRINT OBJECT




#def generateVideo(rtspLink, res, fps, userId):
#
#
#    camera=cv2.VideoCapture(rtspLink)
#    while True:            
#        success = False
#        while success == False: # LOOPS TO ENSURE THAT WE ARE ON THE LAST FRAME
#            success,frame=camera.read() # READS THE CAMERA FRAME
#            if success: # IF THE FRAME IS THE NEWEST
#                ret,buffer=cv2.imencode('.jpg',frame) 
#                frame=buffer.tobytes() # CONVERTS THE FRAME TO A BYTEARRAY
#                
#        yield(b'--frame\r\n'
#                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')





@video.route("/video", methods=["POST","GET"])
@login_required
def videoTable():


    if request.method == "POST":
        if request.form.get("downloadVideoId"):
            pass

        elif request.form.get("deleteVideoId"):

            videoName = request.form.get("deleteVideoName") # GETS THE VIDEO NAME 
            recordingDir = os.path.abspath("website/recordings") # GETS THE FULL RECORDING PATH
            recordingsFile = os.path.join(recordingDir, videoName + ".avi") # ADDS THE VIDEO NAME TO THE RECORDING PATH

            if os.path.exists(recordingsFile): # CHECKS IF THE FILE EXISTS
                  os.remove(recordingsFile) # DELETES THE FILE
            else:
                  logging.critical(f"     Couldnt find the specified avi file to delete: {recordingsFile}")

            con = sqlite3.connect(pathToDB) # CONNECTS TO THE DB
            cursor = con.cursor() # SETS THE CURSOR
            cursor.execute("DELETE FROM 'videos' WHERE id=?", (request.form.get("deleteVideoId"),)) # DELETES THE ROW THAT HAS BEEN PRESSED RELEASED ON
            con.commit() # COMMITS TO THE ACTION
            con.close()

  



    videoItems = selectFromDB(dbPath=pathToDB, table="videos") # GETS ALL OF THE DATA FROM THE TABLE "videos"
    return render_template("video.html", videoItems=videoItems, user=current_user, isAdmin=session.get("isAdmin", False))


@video.route("/rtspStream", methods=["POST","GET"])      
def generateRstpPaths():

    # NOTE NEEED TO FIGURE OUT A WAY FOR ONLY AUTHORIZED USERS TO VIEW THE STREAM 

    rtspLink = "rtsp://root:Troll2014!@192.168.1.21/axis-media/media.amp"
    selectedCamera = selectFromDB(dbPath=pathToDB, table="camera", argumentList=["WHERE"], columnList=["ipAdress"], valueList=[rtspLink])

    while True:
        if selectedCamera[0][3] == True: # CHECKS IF THE RSTP COLUMN IS TRUE
            return Response(stream.generateVideo(),mimetype='multipart/x-mixed-replace; boundary=frame')


@video.route("video/download/<name>")
def downloadVideo(name):
    recordings_dir = os.path.abspath("website/recordings")
    return send_from_directory(recordings_dir, name + ".avi", as_attachment=True)


@video.route('/temperature', methods=['GET']) 
@login_required
def getTemperature():
    process = subprocess.Popen(['vcgencmd', 'measure_temp'], stdout=subprocess.PIPE)
    output, _error = process.communicate()
    temperature = output.decode('UTF-8')

    # The output is in the format of 'temp=XX.X'C, so we will split the string
    temperatureValue = temperature.split('=')[1].split("'")[0]

    return jsonify({'temperature': temperatureValue})











#
#def generateVideo(rtspLink, res, fps, userId):
#
#
#    hasRecorded = False
#    camera=cv2.VideoCapture(rtspLink)
#    while True:
#        startRec = readRecStartVar() == True or readRecStartVar == None and int(time.time() - startTime) < 3600 * 2 # CHECKS IF THE SCRIPT SHULD START RECORDING
#
##------------- WHEN STARTED RECORDING 
#        if startRec == True and hasRecorded == False: # IF WE WANT TO START RECORDING AND WE HAVENT RECORDED A FRAME YET
#            currentTime = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S") # GETS THE CUREENT TIME IN (DAY,MONTH,YEAR HOUR-MINUTE-SECOND) FORMAT
#            name = str(currentTime) # CONVERTS THE DATETIME OBJECT TO A STRING, FOR NAME USAGE
#
#            recDir = os.path.abspath("website/recordings") # FINDS THE FULL PATH TO THE RECORDING DIR
#            recPath = os.path.join(recDir, name + ".avi") # APPENDS THE FILE NAME + THE .avi EXTENTION
#
#            writer = cv2.VideoWriter(recPath, cv2.VideoWriter_fourcc(*'XVID'), fps, res) # MAKES THE VIDEOWRITER OBJECT
#            startTime = time.time() # SETS TGE START TIME, TO CALCULATE THE TOTAL LENGTH OF THE VIDEO
#
#            logging.info("      Started recording!")
#            
#            
#
##------------- WHEN RECORDING
#        success = False
#        while success == False: # LOOPS TO ENSURE THAT WE ARE ON THE LAST FRAME
#            success,frame=camera.read() # READS THE CAMERA FRAME
#            if success: # IF THE FRAME IS THE NEWEST
#                if startRec: # IF THE USER WANTS TO RECORD
#                    writer.write(frame) # WRITES THE FRAME TO THE VIDEOWRITER OBJECT NOTE THE INPUT FPS MUST MATCH THE FPS OF THE CAMERA TO GET CORRECT LENGTH
#                    hasRecorded = True # SAYS THAT WE HAVE RECORDED
#
#                ret,buffer=cv2.imencode('.jpg',frame) 
#                frame=buffer.tobytes() # CONVERTS THE FRAME TO A BYTEARRAY
#                
#
#
##------------- WHEN FINISHED RECORDING
#        if startRec == False and hasRecorded == True: # IF WE ARE NOT RECORDING AND WE HAVE FINISHED RECORDING
#            with app.app_context(): # OPENS WITH APP CONTEXT TO ALLOW TO WRITE TO THE DB
#                elapsedTime = convertSecToHMS(int(time.time() - startTime)) # GETS THE ELAPSED TIME AND RETURNS A STRING IN (hr:min:sec) FORMAT
#                video_ = Videos(userId=userId, fileName=name, duration=elapsedTime) # ADDS THE VIDEO INTO THE DB
#                db.session.add(video_)
#                db.session.commit()   
#
#                writer.release() # CLOSES THE WRITER OBJECT (makes a new one when the user wants to record another video)
#                hasRecorded = False # RESETS THE FINISHED REC VARIABLE
#
#                logging.info("      Stopped recording!")
#
#                
#
#
#        yield(b'--frame\r\n'
#                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#
#
#
#    def recordVideo(rtspLink, res, fps, userId):
#
#        while True: 
#            time.sleep(1)
#            if readRecStartVar() == True or readRecStartVar == None:
#                currentTime = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S") # GETS THE CUREENT TIME IN (DAY,MONTH,YEAR HOUR-MINUTE-SECOND) FORMAT
#                name = str(currentTime) # CONVERTS THE DATETIME OBJECT TO A STRING, FOR NAME USAGE
#
#                recDir = os.path.abspath("website/recordings") # FINDS THE FULL PATH TO THE RECORDING DIR
#                recPath = os.path.join(recDir, name + ".avi") # APPENDS THE FILE NAME + THE .avi EXTENTION
#
#                writer = cv2.VideoWriter(recPath, cv2.VideoWriter_fourcc(*'XVID'), fps, res) # MAKES THE VIDEOWRITER OBJECT
#                startTime = time.time() # SETS TGE START TIME, TO CALCULATE THE TOTAL LENGTH OF THE VIDEO
#
#                camera=cv2.VideoCapture(rtspLink)
#
#                logging.info("      Started recording!")
#
#                while readRecStartVar() == True or readRecStartVar == None and int(time.time() - startTime) < 3600 * 2:
#                    success,frame=camera.read() # READS THE CAMERA FRAME
#                    if success: # IF THE FRAME IS THE NEWEST
#                        writer.write(frame) # WRITES THE FRAME TO THE VIDEOWRITER OBJECT NOTE THE INPUT FPS MUST MATCH THE FPS OF THE CAMERA TO GET CORRECT LENGTH
#
#
#
#                with app.app_context(): # OPENS WITH APP CONTEXT TO ALLOW TO WRITE TO THE DB
#                    elapsedTime = convertSecToHMS(int(time.time() - startTime)) # GETS THE ELAPSED TIME AND RETURNS A STRING IN (hr:min:sec) FORMAT
#                    video_ = Videos(userId=userId, fileName=name, duration=elapsedTime) # ADDS THE VIDEO INTO THE DB
#                    db.session.add(video_)
#                    db.session.commit()   
#
#                    writer.release() # CLOSES THE WRITER OBJECT (makes a new one when the user wants to record another video)
#                    logging.info("      Stopped recording!")
