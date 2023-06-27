from ..dbService import addVideo
from threading import Event

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
___________________________________ readRecStartVar ___________________________________
This function reads the start variable in "instance/startRecord.json". 
The varaible determens if i shuld keep/start recording

"""
def readRecStartVar():
    instanceDir = os.path.abspath("instance") # GETS THE FULL PATH OF THE INSTANCE DIRECTORY
    recJsonPath = instanceDir + "/startRecord.json" # MAKES THE FULL PATH TO THE JOSN FILE


    try:  # IT IS IN A TRY/EXCEPT STATMENT, BECAUSE SOMETIMES IS THERE A PROBLEM THAT SOMEONE ELSE IS READING/WRITING TO THE JSON FILE, CAUSING AN ERROR
        with open(recJsonPath) as f: # OPENS THE JSON FILE
            data = json.load(f) # LOADS THE DATA
    except:
        return None # RETURNS NONE IF ERROR

    return  data["startRec"] # RETURNS THE STARTREC VALUE (True or False)


class RtspStream():
    def __init__(self, db, app, logging, rtspLink, res, fps, userId):
        
        self.rtspLink = rtspLink
        self.res = res
        self.fps = fps

        self.userId = userId
        self.frame = None

        self.db = db
        self.app = app
        self.logging = logging

        self.frameEvent = Event()

        self.camera=cv2.VideoCapture(rtspLink)

    def readFrame(self): # THIS FUNCTION READS ALL OF THE FRAMES COMING FROM THE RTSP STREAM

        while True: # WHILE SUCSESS == FALSE
            success, self.frame = self.camera.read() 
            self.frameEvent.set()




    def recordVideo(self): # THIS FUNCTION RECORDS VIDEOS, AND GETS FRAMES THAT IS READ FROM "readFrame" FUNCTION (self.frame)
        while True: # LOOPS INFINATLY
            time.sleep(1)
            if readRecStartVar() == True: # CHECKS IF THE USER WANTS TO START RECORDING
                currentTime = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S") # GETS THE CUREENT TIME IN (DAY,MONTH,YEAR HOUR-MINUTE-SECOND) FORMAT
                name = str(currentTime) # CONVERTS THE DATETIME OBJECT TO A STRING, FOR NAME USAGE

                recDir = os.path.abspath("website/recordings") # FINDS THE FULL PATH TO THE RECORDING DIR
                recPath = os.path.join(recDir, name + ".avi") # APPENDS THE FILE NAME + THE .avi EXTENTION

                writer = cv2.VideoWriter(recPath, cv2.VideoWriter_fourcc(*'XVID'), self.fps, self.res) # MAKES THE VIDEOWRITER OBJECT
                startTime = time.time() # SETS TGE START TIME, TO CALCULATE THE TOTAL LENGTH OF THE VIDEO

                self.logging.info("      Started recording!") # LOGS THE ACTION, USEFUL FOR DEBUGGUNG
        

                
                while readRecStartVar() == True or readRecStartVar() == None and int(time.time() - startTime) < 3600 * 100: # WHILE THE "startRec" VALUE FROM THE JSON FILE IS TRUE OR RETURNS NONE (error reading), AND IT HAS GONE LESS THAN 100 HRS
                    self.frameEvent.wait() # WAITS FOR A NEW FRAME EVENT
                    writer.write(self.frame) # WRITES THE FRAME TO THE VIDEOWRITER OBJECT NOTE THE INPUT FPS MUST MATCH THE FPS OF THE CAMERA TO GET CORRECT LENGTH
                    self.frameEvent.clear()


                # NOTE ADDS TWO VIDEOS TO THE DB FOR SOME REASON
                elapsedTime = convertSecToHMS(int(time.time() - startTime)) # GETS THE ELAPSED TIME AND RETURNS A STRING IN (hr:min:sec) FORMAT        
                addVideo(self.app, self.userId, name, elapsedTime)
        
                writer.release() # CLOSES THE WRITER OBJECT (makes a new one when the user wants to record another video)


    def generateVideo(self): # THIS FUNCTION GENERATES THE VIDEO, THAT CAN BE LIVE VIEWED BY THE USER, REUTRNS A GENERATOR OBJECT

 


        while True: 
            self.frameEvent.wait() # WAITS FOR A NEW FRAME EVENT
            ret, buffer = cv2.imencode(".jpg", self.frame) # CONVERTS THE IMAGE TO A MEMORY BUFFER
            byteArr=buffer.tobytes() # CONVERTS THE FRAME TO A BYTEARRAY
            self.frameEvent.clear() # SAYS IT HAS GOTTEN A NEW FRAME EVENT


            yield(b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + byteArr + b'\r\n')
