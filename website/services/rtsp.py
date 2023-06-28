from ..services.dbService import addRowToTable
from threading import Event

from ..models import Videos
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
___________________________________ convertSecToHMS ___________________________________
This function converts seconds to HR:MIN:SEC format

Seconds = This is the amout of seconds you want to change to H:M:S format

"""
def convertSecToHMS(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))


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
    stream = RtspStream(db, app, logger, rtspLink, res,  fps,  userId, recordingsFolder)
    threading.Thread(target=stream.readFrame, args=()).start()
    time.sleep(0.5)
    threading.Thread(target=stream.recordVideo, args=()).start()
    return stream


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
        self.startRecoring = False

        self.camera=cv2.VideoCapture(rtspLink)

    def readFrame(self): # THIS FUNCTION READS ALL OF THE FRAMES COMING FROM THE RTSP STREAM

        while True: # WHILE SUCSESS == FALSE
            success, self.frame = self.camera.read() 
            self.frameEvent.set()



    def recordVideo(self): # THIS FUNCTION RECORDS VIDEOS, AND GETS FRAMES THAT IS READ FROM "readFrame" FUNCTION (self.frame)
        while True: # LOOPS INFINATLY
            time.sleep(1)
            if self.startRecoring: # CHECKS IF THE USER WANTS TO START RECORDING
                currentTime = datetime.datetime.now().strftime(config.videoTimeFormat) # GETS THE CUREENT TIME IN (DAY,MONTH,YEAR HOUR-MINUTE-SECOND) FORMAT
                name = str(currentTime) # CONVERTS THE DATETIME OBJECT TO A STRING, FOR NAME USAGE

                recDir = os.path.abspath(self.recordingsFolder) # FINDS THE FULL PATH TO THE RECORDING DIR
                recPath = os.path.join(recDir, name + ".avi") # APPENDS THE FILE NAME + THE .avi EXTENTION

                writer = cv2.VideoWriter(recPath, cv2.VideoWriter_fourcc(*'XVID'), self.fps, self.res) # MAKES THE VIDEOWRITER OBJECT
                startTime = time.time() # SETS TGE START TIME, TO CALCULATE THE TOTAL LENGTH OF THE VIDEO

                self.logging.info("      Started recording!") # LOGS THE ACTION, USEFUL FOR DEBUGGUNG
        

                
                while self.startRecoring and int(time.time() - startTime) < 3600 * 100: # WHILE THE "startRec" VALUE FROM THE JSON FILE IS TRUE OR RETURNS NONE (error reading), AND IT HAS GONE LESS THAN 100 HRS
                    self.frameEvent.wait() # WAITS FOR A NEW FRAME EVENT
                    writer.write(self.frame) # WRITES THE FRAME TO THE VIDEOWRITER OBJECT NOTE THE INPUT FPS MUST MATCH THE FPS OF THE CAMERA TO GET CORRECT LENGTH
                    self.frameEvent.clear()

                elapsedTime = convertSecToHMS(int(time.time() - startTime)) # GETS THE ELAPSED TIME AND RETURNS A STRING IN (hr:min:sec) FORMAT        
                addRowToTable(Videos, {"userId": self.userId, "fileName": name, "duration": elapsedTime}, self.app)
                self.startRecoring = False
                writer.release() # CLOSES THE WRITER OBJECT (makes a new one when the user wants to record another video)


    def generateVideo(self): # THIS FUNCTION GENERATES THE VIDEO, THAT CAN BE LIVE VIEWED BY THE USER, REUTRNS A GENERATOR OBJECT

 
        while True: 
            self.frameEvent.wait() # WAITS FOR A NEW FRAME EVENT
            ret, buffer = cv2.imencode(".jpg", self.frame) # CONVERTS THE IMAGE TO A MEMORY BUFFER
            byteArr=buffer.tobytes() # CONVERTS THE FRAME TO A BYTEARRAY
            self.frameEvent.clear() # SAYS IT HAS GOTTEN A NEW FRAME EVENT

            yield(b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + byteArr + b'\r\n')
