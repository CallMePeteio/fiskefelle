from ..services.dbService import addRowToTable
from .miscServices import convertSecToHMS
from threading import Event

from ..models import Videos
from .. import logging
from .. import config
from .. import app
from .. import db

import threading
import datetime
import numpy
import time
import json
import cv2
import os



"""
______________________________________ getDirSize _____________________________________
This function gets the file size inside a certian directory.
It returns an integer that is the size of the element sin the dir in GB

start_path = This is the full path to the directory you want to get the size of

"""
def getDirSize(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)


    size_in_gb = round(total_size / 1073741824, 2)  # Convert bytes to gigabytes
    return size_in_gb



def startRtspStream(db, app, logger, rtspLink, res, fps, userId, recordingsFolder):
    logger.info("    Started Rtsp Stream!")


    def startThreads():
        stream = RtspStream(db, app, logger, rtspLink, res,  fps,  userId, recordingsFolder)
        threading.Thread(target=stream.readFrame, args=()).start()
        threading.Thread(target=stream.recordVideo, args=()).start()
        threading.Thread(target=stream.checkError, args=()).start()

        app.stream = stream

    threading.Thread(target=startThreads, args=()).start()
    


def stopRtspStream(stream): 
    app.stream = None
    stream.run = False 
    logging.info("    Stopped Rtsp Stream!")





class RtspStream():
    def __init__(self, db, app, logging, rtspLink, res, fps, userId, recordingsFolder):
        
        self.recordingsFolder = recordingsFolder
        self.rtspLink = rtspLink
        self.res = res
        self.fps = fps

        self.userId = userId
        self.frame = None

        self.db = db
        self.app = app
        self.logging = logging

        self.frameEvent = Event()
        self.isReadingFrames = False
        self.startRecoring = False
        self.error = False
        self.run = True

        self.camera=cv2.VideoCapture(rtspLink)

        if not self.camera.isOpened(): 
            self.error = True


    def readFrame(self): # THIS FUNCTION READS ALL OF THE FRAMES COMING FROM THE RTSP STREAM

        while self.run and self.error == False: # WHILE IT SHULD RUN
            success, self.frame = self.camera.read() 
            self.frameEvent.set()
            self.isReadingFrames = True

        self.camera.release()


    def recordVideo(self): # THIS FUNCTION RECORDS VIDEOS, AND GETS FRAMES THAT IS READ FROM "readFrame" FUNCTION (self.frame)
        while self.run and self.error == False: # LOOPS INFINATLY
            time.sleep(1)
            if self.startRecoring: # CHECKS IF THE USER WANTS TO START RECORDING
                currentTime = datetime.datetime.now().strftime(config.videoTimeFormat) # GETS THE CUREENT TIME IN (DAY,MONTH,YEAR HOUR-MINUTE-SECOND) FORMAT
                name = str(currentTime) # CONVERTS THE DATETIME OBJECT TO A STRING, FOR NAME USAGE

                recDir = os.path.abspath(self.recordingsFolder) # FINDS THE FULL PATH TO THE RECORDING DIR
                recPath = os.path.join(recDir, name + ".avi") # APPENDS THE FILE NAME + THE .avi EXTENTION

                writer = cv2.VideoWriter(recPath, cv2.VideoWriter_fourcc(*'XVID'), self.fps, self.res) # MAKES THE VIDEOWRITER OBJECT
                startTime = time.time() # SETS TGE START TIME, TO CALCULATE THE TOTAL LENGTH OF THE VIDEO

                self.logging.info("      Started recording!") # LOGS THE ACTION, USEFUL FOR DEBUGGUNG
        

                
                while self.startRecoring and self.run and int(time.time() - startTime) < 3600 * 100: # WHILE THE "startRec" VALUE FROM THE JSON FILE IS TRUE OR RETURNS NONE (error reading), AND IT HAS GONE LESS THAN 100 HRS
                    self.frameEvent.wait() # WAITS FOR A NEW FRAME EVENT
                    writer.write(self.frame) # WRITES THE FRAME TO THE VIDEOWRITER OBJECT NOTE THE INPUT FPS MUST MATCH THE FPS OF THE CAMERA TO GET CORRECT LENGTH
                    self.frameEvent.clear()

                elapsedTime = convertSecToHMS(int(time.time() - startTime)) # GETS THE ELAPSED TIME AND RETURNS A STRING IN (hr:min:sec) FORMAT        
                addRowToTable(Videos, {"userId": self.userId, "fileName": name, "duration": elapsedTime}, self.app)
                self.startRecoring = False
                writer.release() # CLOSES THE WRITER OBJECT (makes a new one when the user wants to record another video)


    def generateVideo(self): # THIS FUNCTION GENERATES THE VIDEO, THAT CAN BE LIVE VIEWED BY THE USER, REUTRNS A GENERATOR OBJECT
        while self.run and self.error == False: 
            self.frameEvent.wait() # WAITS FOR A NEW FRAME EVENT
            ret, buffer = cv2.imencode(".jpg", self.frame) # CONVERTS THE IMAGE TO A MEMORY BUFFER
            byteArr=buffer.tobytes() # CONVERTS THE FRAME TO A BYTEARRAY
            self.frameEvent.clear() # SAYS IT HAS GOTTEN A NEW FRAME EVENT

            yield(b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + byteArr + b'\r\n')
    
    def checkError(self): 
        while self.error == True and self.run == True:  # KEEPS THE APP ALIVE, SO I CAN CHECK self.error
            time.sleep(5)



