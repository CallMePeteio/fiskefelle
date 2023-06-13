
from flask import render_template
from flask import Blueprint
from flask import Response
from flask import session

from . import selectFromDB
from . import pathToDB

import threading 
import cv2


rstp = Blueprint('rstp', __name__) # MAKES THE BLUPRINT OBJECT


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



@rstp.route("/rstpStream", methods=["POST","GET"])         
def generateRstpPaths(): 

    selectedCamera = selectFromDB(dbPath=pathToDB, table="camera", argumentList=["WHERE"], columnList=["ipAdress"], valueList=[session["selectedCamIp"]])

    prevCamIp = session["selectedCamIp"]

    while True: 
        if selectedCamera[0][3] == True: # CHECKS IF THE RSTP COLUMN IS TRUE
            videoStream = rstpStream(selectedCamera[0][5])  # Create a VideoCamera object

            threading.Thread(target=videoStream.capture_frame, args=()).start()  # Start video capture thread

            return Response(videoStream.generate(),  # Call the generator method on `video_stream`
                            mimetype='multipart/x-mixed-replace; boundary=frame')

