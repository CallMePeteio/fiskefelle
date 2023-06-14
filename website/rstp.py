
from flask import render_template
from flask import Blueprint
from flask import Response
from flask import session

from . import selectFromDB
from . import pathToDB

import threading 
import cv2


rstp = Blueprint('rstp', __name__) # MAKES THE BLUPRINT OBJECT


class rtspStream(object):
    def __init__(self, rtsp_url):
        self.video = cv2.VideoCapture(rtsp_url)  # Create a VideoCapture object with the given RTSP URL
        if not self.video.isOpened():  # Check if video stream opened successfully
            print("Failed to open the RTSP stream.")
            exit()

        self.frame = None  # Current frame
        self.lock = threading.Lock()  # Lock to synchronize access to `self.frame`
        self.is_running = True  # Control the running of the capture frame loop

    def capture_frame(self):
        while self.is_running:  # Read the next frame while `self.is_running` is True
            ret, frame = self.video.read()
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

    def stop(self):  # Add a stopping function
        self.is_running = False  # Set `self.is_running` to False to stop the `capture_frame` loop
        self.video.release()  # Release the VideoCapture object



def returnIpAdress(name):

    findportStart = name.rfind(":")
    findIpAddrStart = name.rfind("@")
    return name[findIpAddrStart +1:findportStart]


@rstp.route("/rstp", methods=["POST","GET"])
def generateRstpPaths(): 
    cameras = selectFromDB(pathToDB, "camera")

    for camera in cameras:
        if camera[3] == 1: # IF THE CAMERA IS RSTP

            cameraIpAdress = returnIpAdress(camera[5])
            videoStream = rtspStream(cameraIpAdress)  # Create a VideoCamera object

    return render_template("basic.html")

    





#
    #while True:
#
    #    if selectedCamera[0][3] == True: # CHECKS IF THE RSTP COLUMN IS TRUE
    #        videoStream = rtspStream(selectedCamera[0][5])  # Create a VideoCamera object
    #        print("CONTINUE")
    #        threading.Thread(target=videoStream.capture_frame, args=()).start()  # Start video capture thread
    #        return Response(videoStream.generate(),  # Call the generator method on `video_stream`
    #                        mimetype='multipart/x-mixed-replace; boundary=frame')
        






