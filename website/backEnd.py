
from flask import Blueprint, render_template, request, flash, session
from flask import jsonify

from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

import subprocess



backEnd = Blueprint('backEnd', __name__) # MAKES THE BLUPRINT OBJECT

@backEnd.route('/cameraJson', methods=['GET'])
@login_required
def cameraJson():
    cameraTable = session.get("cameraTable", False)

    if cameraTable == False or cameraTable == None: # IF THERE ISNT ANY CAMERAS
        cameraTable = {"camera": 'null'} # RETURNS NULL

    return str(cameraTable)


@backEnd.route('/temperature', methods=['GET']) 
@login_required
def getTemperature():
    process = subprocess.Popen(['vcgencmd', 'measure_temp'], stdout=subprocess.PIPE)
    output, _error = process.communicate()
    temperature = output.decode('UTF-8')

    temperatureValue = temperature.split('=')[1].split("'")[0] # The output is in the format of 'temp=XX.X'C, so we will split the string

    return jsonify({'temperature': temperatureValue})


