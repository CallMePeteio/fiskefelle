from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from multiprocessing import Process
import threading 
import uvicorn
import cv2
import numpy as np

import time 
#
#class rtspStream(object):
#    def __init__(self, rtsp_url, port):
#        self.video = cv2.VideoCapture(rtsp_url)  # Initialize the VideoCapture with RTSP url
#        if not self.video.isOpened():  # If video stream did not open successfully
#            print("Failed to open the RTSP stream.")
#            exit()
#
#        self.frame = None  # Will hold the current frame 
#        self.lock = threading.Lock()  # Lock to synchronize access to `self.frame`
#        self.is_running = True  # Control the running of the capture frame loop
#
#        threading.Thread(target=self.capture_frame, args=()).start()  # Start the frame capture thread
#        time.sleep(0.5)
#        Process(target=self.start_server, args=(port,)).start()  # Start a new process for each RTSP stream
#
#    def capture_frame(self):
#        while self.is_running:  # Loop while the stream is running
#            ret, frame = self.video.read()  # Read the next frame from the video
#            if not ret:  # If reading the frame failed
#                print("Failed to grab frame.")
#                break
#
#            with self.lock:  # Access `self.frame` in a thread-safe manner
#                self.frame = frame  # Update the current frame
#
#            self.video.grab()  # Discard any buffered frames
#
#    def get_frame(self):
#        with self.lock:  # Access `self.frame` in a thread-safe manner
#            if self.frame is not None:  # If a frame is available
#                ret, jpeg = cv2.imencode('.jpg', self.frame)  # Encode the frame as JPEG
#                if ret:  # If encoding was successful
#                    return jpeg.tobytes()  # Return the encoded frame
#
#    def generate(self):
#        while True:  # Infinite loop to continuously serve frames
#            frame = self.get_frame()  # Get the current frame
#            if frame is not None:  # If a frame is available
#                yield (b'--frame\r\n'
#                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # Yield the frame for HTTP response
#
#    def stop(self):
#        self.is_running = False  # Stop the capture frame loop
#        self.video.release()  # Release the VideoCapture object
#
#    def start_server(self, port):
#        app = FastAPI()  # Create a FastAPI application
#
#        @app.get("/")  # Define a route for the FastAPI application
#        async def main():
#            return StreamingResponse(self.generate(), media_type="multipart/x-mixed-replace; boundary=frame")  # Stream the frames as HTTP response
#
#        uvicorn.run(app, host="0.0.0.0", port=port)  # Start the FastAPI server on the specified port
#
#
#if __name__ == "__main__":
#    streams = [("rtsp://admin:Troll2014@192.168.1.20:554", 8000)]  # List of RTSP URLs and ports
#
#
#    for rtsp_url, port in streams:  # For each RTSP URL and port
#        rtspStream(rtsp_url, port)  # Create an instance of `rtspStream`
#        print(rtsp_url, port)
#




import cv2
import rtsp

stream = rtsp.Client(rtsp_server_uri = 'rtsp://admin:Troll2014@192.168.1.20:554')

while True:
    image = stream.read()
    if image is None:
        break
    else:
        cv2.imshow("Video Stream", image)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # press 'q' to exit the video stream
            break
stream.close()
cv2.destroyAllWindows()
