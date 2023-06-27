
from flask import Blueprint, render_template, request, flash, session
from flask import send_from_directory
from flask import jsonify

from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from ..services.rtsp import getDirSize

from .. import config 

import subprocess
import os



api = Blueprint('api', __name__) # MAKES THE BLUPRINT OBJECT

@api.route('/cameraJson', methods=['GET'])
@login_required
def cameraJson():
    cameraTable = session.get("cameraTable", False)

    if cameraTable == False or cameraTable == None: # IF THERE ISNT ANY CAMERAS
        cameraTable = {"camera": 'null'} # RETURNS NULL

    return str(cameraTable)


@api.route('/temperature', methods=['GET']) 
@login_required
def getTemperature():
    process = subprocess.Popen(['vcgencmd', 'measure_temp'], stdout=subprocess.PIPE)
    output, _error = process.communicate()
    temperature = output.decode('UTF-8')

    temperatureValue = temperature.split('=')[1].split("'")[0] # The output is in the format of 'temp=XX.X'C, so we will split the string

    return jsonify({'temperature': temperatureValue})


@api.route("video/download/<name>")
def downloadVideo(name):
    recordings_dir = os.path.abspath(config.recordingsFolder)
    return send_from_directory(recordings_dir, name + ".avi", as_attachment=True)


@api.route("/usedVidSpace", methods=["GET"])
@login_required
def getUsedVidSpace():
    recDir = os.path.abspath(config.recordingsFolder) # FINDS THE FULL PATH TO THE RECORDING DIR
    recDirSize = getDirSize(recDir)

    return jsonify({"usedSpace": recDirSize, "maxSpace": config.maxRecordSizeGB})
