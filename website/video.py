
from flask_login import login_required
from flask_login import current_user

from flask import send_from_directory
from flask import render_template
from flask import Blueprint
from flask import Response
from flask import session
from flask import request


from .models import Videos

from . import selectFromDB
from . import pathToDB
from . import db

import threading 
import datetime
import sqlite3
import time
import cv2
import os 


video = Blueprint('video', __name__) # MAKES THE BLUPRINT OBJECT


class rstpStream(object):
    def __init__(self, rtsp_url):
        self.video = cv2.VideoCapture(rtsp_url)  # Create a VideoCapture object with the given RTSP URL
        if not self.video.isOpened():  # Check if video stream opened successfully
            print("Failed to open the RTSP stream.")
            exit()

        self.frame = None  # Current frame
        self.lock = threading.Lock()  # Lock to synchronize access to `self.frame`

    def capture_frame(self):
        while True:  
            ret, frame = self.video.read()  # Read the next frame
            if not ret:  # If reading frame failed, break the loop
                print("Failed to grab frame.")
                break
            with self.lock:  # Synchronize access to `self.frame`
                self.frame = frame  # Update current frame
            self.video.grab()  # Discard any buffered frames

    def get_frame(self):
        with self.lock:  # Synchronize access to `self.frame`
            if self.frame is not None:  # If a frame is available
                ret, jpeg = cv2.imencode('.jpg', self.frame)  # Encode frame as JPEG
                if ret:  # If encoding was successful, return the encoded frame
                    return jpeg.tobytes()

    def generate(self):
        """Video streaming generator function."""
        while True:  # Infinite loop to continuously serve frames
            frame = self.get_frame()  # Get the current frame
            if frame is not None:  # If a frame is available
                # Yield the frame as part of a multipart HTTP response
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')




@video.route("/video", methods=["POST","GET"])
@login_required
def videoTable():


    if request.method == "POST":
        if request.form.get("downloadVideoId"):
            

            pass



    
        elif request.form.get("deleteVideoId"):

            videoName = request.form.get("deleteVideoName") # GETS THE VIDEO NAME 
            recordingDir = os.path.abspath("website/recordings") # GETS THE FULL RECORDING PATH
            recordingsFile = os.path.join(recordingDir, videoName + ".mp4") # ADDS THE VIDEO NAME TO THE RECORDING PATH

            if os.path.exists(recordingsFile): # CHECKS IF THE FILE EXISTS
                  os.remove(recordingsFile) # DELETES THE FILE



            con = sqlite3.connect(pathToDB) # CONNECTS TO THE DB
            cursor = con.cursor() # SETS THE CURSOR
            cursor.execute("DELETE FROM 'videos' WHERE id=?", (request.form.get("deleteVideoId"),)) # DELETES THE ROW THAT HAS BEEN PRESSED RELEASED ON
            con.commit() # COMMITS TO THE ACTION
            con.close()

            # NEED TO ADD SO IT DELETES THE VIDEO FROM THE RASPBERRY PI 




    videoItems = selectFromDB(dbPath=pathToDB, table="videos") # GETS ALL OF THE DATA FROM THE TABLE "videos"
    return render_template("video.html", videoItems=videoItems)

def convertSecToHMS(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))


def recordRtspStream(link, res, fps, userId, setNameAsDate=True, name=None, writeToDB=True): 


    if setNameAsDate == True and name == None: 
        currentTime = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S") # GETS THE CUREENT TIME IN (DAY,MONTH,YEAR HOUR-MINUTE-SECOND) FORMAT
        name = str(currentTime)        

    # open video stream
    cap = cv2.VideoCapture(link)

    # set video codec
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    recordings_dir = os.path.abspath("website/recordings")
    recordings_dir = os.path.join(recordings_dir, name + ".mp4")
    out = cv2.VideoWriter(recordings_dir, fourcc, fps, res)

    # start timer
    start_time = time.time()    

    while (int(time.time() - start_time) < 3):
        ret, frame = cap.read() 
        if ret == True:
            out.write(frame)
        else:
            break

    elapsedTime = convertSecToHMS(int(time.time() - start_time)) # GETS THE ELAPSED TIME AND RETURNS A STRING IN (hr:min:sec) FORMAT
    video_ = Videos(userId=userId, fileName=name, duration=elapsedTime) # ADDS THE VIDEO INTO THE DB
    db.session.add(video_)
    db.session.commit()                    
    
    cap.release()
    out.release()

    

@video.route("/rtspStream", methods=["POST","GET"])    
@login_required   
def generateRstpPaths(): 


    rtspLink = "rtsp://admin:Troll2014@192.168.1.20:554"
    selectedCamera = selectFromDB(dbPath=pathToDB, table="camera", argumentList=["WHERE"], columnList=["ipAdress"], valueList=[rtspLink])

    recordRtspStream(rtspLink, (1280, 720), 18, current_user.id)


    return render_template("basic.html")


@video.route("video/download/<name>")
def downloadVideo(name):
    recordings_dir = os.path.abspath("website/recordings")
    #recordings_dir = os.path.join(recordings_dir, name + ".mp4")


    return send_from_directory(recordings_dir, name + ".mp4", as_attachment=True)


#
    #while True: 
    #    if selectedCamera[0][3] == True: # CHECKS IF THE RSTP COLUMN IS TRUE
    #        videoStream = rstpStream(selectedCamera[0][5])  # Create a VideoCamera object
#
    #        threading.Thread(target=videoStream.capture_frame, args=()).start()  # Start video capture thread
#
    #        return Response(videoStream.generate(),  # Call the generator method on `video_stream`
    #                        mimetype='multipart/x-mixed-replace; boundary=frame')
#



#from flask import render_template
#from flask import Blueprint
#from flask import Response
#from flask import session
#
#from . import selectFromDB
#from . import pathToDB
#
#import threading 
#import cv2
#
#
#rstp = Blueprint('rstp', __name__) # MAKES THE BLUPRINT OBJECT
#
#
#class rtspStream(object):
#    def __init__(self, rtsp_url):
#        self.video = cv2.VideoCapture(rtsp_url)  # Create a VideoCapture object with the given RTSP URL
#        if not self.video.isOpened():  # Check if video stream opened successfully
#            print("Failed to open the RTSP stream.")
#            exit()
#
#        self.frame = None  # Current frame
#        self.lock = threading.Lock()  # Lock to synchronize access to `self.frame`
#        self.is_running = True  # Control the running of the capture frame loop
#
#    def capture_frame(self):
#        while self.is_running:  # Read the next frame while `self.is_running` is True
#            ret, frame = self.video.read()
#            if not ret:  # If reading frame failed, break the loop
#                print("Failed to grab frame.")
#                break
#            with self.lock:  # Synchronize access to `self.frame`
#                self.frame = frame  # Update current frame
#            self.video.grab()  # Discard any buffered frames
#
#    def get_frame(self):
#        with self.lock:  # Synchronize access to `self.frame`
#            if self.frame is not None:  # If a frame is available
#                ret, jpeg = cv2.imencode('.jpg', self.frame)  # Encode frame as JPEG
#                if ret:  # If encoding was successful, return the encoded frame
#                    return jpeg.tobytes()
#
#    def generate(self):
#        """Video streaming generator function."""
#        while True:  # Infinite loop to continuously serve frames
#            frame = self.get_frame()  # Get the current frame
#            if frame is not None:  # If a frame is available
#                # Yield the frame as part of a multipart HTTP response
#                yield (b'--frame\r\n'
#                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#
#    def stop(self):  # Add a stopping function
#        self.is_running = False  # Set `self.is_running` to False to stop the `capture_frame` loop
#        self.video.release()  # Release the VideoCapture object
#
#
#
#def returnIpAdress(name):
#
#    findportStart = name.rfind(":")
#    findIpAddrStart = name.rfind("@")
#    return name[findIpAddrStart +1:findportStart]
#
#
#@rstp.route("/rstp", methods=["POST","GET"])
#def generateRstpPaths(): 
#    cameras = selectFromDB(pathToDB, "camera")
#
#    selectedCamera = selectFromDB(dbPath=pathToDB, table="camera", argumentList=["WHERE"], columnList=["ipAdress"], valueList=[session["selectedCamIp"]])
#
#
##
#    while True: 
#        if selectedCamera[0][3] == True: # CHECKS IF THE RSTP COLUMN IS TRUE
#            videoStream = rtspStream(selectedCamera[0][5])  # Create a VideoCamera object
#            print("CONTINUE")
#            threading.Thread(target=videoStream.capture_frame, args=()).start()  # Start video capture thread
#            return Response(videoStream.generate(),  # Call the generator method on `video_stream`
#                            mimetype='multipart/x-mixed-replace; boundary=frame')
#        
#
#
#
#


#    for camera in cameras:
#        #if camera[3] == 1: # IF THE CAMERA IS RSTP
#
#            cameraIpAdress = returnIpAdress(camera[5]) # GETS THE RAW IP ADRESS FROM THE WHOLE URL
#            print(cameraIpAdress)
#            #@rstp.route(f"/{cameraIpAdress}")
##
#            #def show(cameraIpAdress=cameraIpAdress):
#            #    videoStream = rtspStream(camera[5])  # Create a VideoCamera object
##
#            #    return "You acsessed %s" % cameraIpAdress
#            #
#
#
#
#
#    return render_template("basic.html")
#
#    
#
#
#
#
#
##
#    #while True:
##
#    #    if selectedCamera[0][3] == True: # CHECKS IF THE RSTP COLUMN IS TRUE
#    #        videoStream = rtspStream(selectedCamera[0][5])  # Create a VideoCamera object
#    #        print("CONTINUE")
#    #        threading.Thread(target=videoStream.capture_frame, args=()).start()  # Start video capture thread
    #        return Response(videoStream.generate(),  # Call the generator method on `video_stream`
    #                        mimetype='multipart/x-mixed-replace; boundary=frame')
        






