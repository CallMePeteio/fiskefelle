
from flask import Blueprint, render_template, request, flash, session
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash




backEnd = Blueprint('backEnd', __name__) # MAKES THE BLUPRINT OBJECT

@backEnd.route('/cameraJson', methods=['GET'])
@login_required
def cameraJson():
    cameraTable = session.get("cameraTable", False)

    if cameraTable == False or cameraTable == None: # IF THERE ISNT ANY CAMERAS
        cameraTable = {"camera": 'null'} # RETURNS NULL

    return str(cameraTable)




