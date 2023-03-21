from flask import Blueprint, render_template, request, flash, session
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from . import getNameAndAdminCamera
from . import selectFromDB
from .models import Camera
from .models import User
from .models import Log
from . import pathToDB
from . import logging 
from . import db
import sqlite3
import json

views = Blueprint('views', __name__)


def logAction(userId, openDoor, turnLights): 
    log = Log(userId=userId, openDoor=openDoor, turnLights=turnLights)
    db.session.add(log)
    db.session.commit()


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():

    if request.method == "POST": 
        if request.form.get("gate") == "open":
            logging.info("   Open the gates!")
            logAction(current_user.id, True, False)

        elif request.form.get("gate") == "close":
            logging.info("   Close the gates!")
            logAction(current_user.id, False, False)


        elif request.form.get("camera"):
            logging.info(f"     Showing camera with id: {id}")

            camId = request.form.get("camera")
            camRow = selectFromDB(dbPath=pathToDB, table="camera", argumentList=["WHERE"], columnList=["id"], valueList=camId)
            session["currentVidIp"] = camRow[0][3]


        """
        NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE
        
        BECAUSE WHAT IS SELECTED IS SAVED IN session["currentVidIp"] THEN THIS VARAIBLE WILL UPDATE AND THE THINGS WILL GET FUCKED, NEED TO MAKE EATCH SESSION INDEPENDENT

        NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE
        """


    logging.warning(session.get("currentViewId", False))
    print(getNameAndAdminCamera(session.get("cameraTable", False)))
    return render_template("home.html", user=current_user, isAdmin=session.get("isAdmin", False), cameraName=getNameAndAdminCamera(session.get("cameraTable", False)), cameraData=session.get("cameraTable", False), camIp=session.get("currentVidIp", False))





def checkEmailAndPassword(email, password): 
    user = User.query.filter_by(email=email).first()
    if user:
        flash('Email already exists.', category='error')
    elif len(email) < 4:
        flash('Email must be greater than 3 characters.', category='error')
    elif len(password) < 7:
        flash('Password must be at least 7 characters.', category='error')
    else:
        flash("Sucsessfully made a new user!")
        return True
    return False
def checkNameAndIp(name, ip): 

    # NOTE WHEN CHECKING THE IP ADRESS OF A CAMERA I NEED TO CHECK IF THEY ENTERED A PORT


#    ipList = ip.split(".") # RETURNS A LIST: ["10", "0", "0", "45:8000"]
#    lastList = ip[len(ipList) -1].split(":") # SPLITS THE LAST ELEMENTS: ["45", "8000"]
#    ip = ipList[:len(ipList) -1] # REMOVES THE LAST ELEMENT, FROM THE LIST ("45:8000")
#    ip.extend([lastList[0]]) # EXTENDS THE IP LIST WITH THE LAST LIST ["10", "0", "0", "45"]
#    #port = lastList[1]
#    isGood = all(len(ip_) in (1,2,3) for ip_ in ip) # CHECKS IF THE LENGTH OF ANY OF THE INTEGERS IS SMALLER THAN 1 OR GREATER THAT 

    ipNum = ip.replace(".", "")
    ipNum = ipNum.replace(":", "")

    if len(name) > 130: 
        flash("Name cant be greater than 130 charachters", category='error')
    elif ip.count(".") < 3: 
        flash(f"Invalid ip adress entered: {ip}", category='error')
        return False 
    elif ip.find(":") == -1: 
        flash("You also need to enter the port on the ip adress, example: 10.0.0.45:8000", category='error')

    #elif isGood == True:
    #    flash(f"The ip adress integers cant contain more than three charachters: {ip}", category='error')
    #
    #elif len(port) >= 4:
    #    flash(f"Error with the length of the port: {port}", category='error')

    if ipNum.isdigit() == False: 
        flash(f"The ip adress cant contain letters, ip adress: {ip}", category='error')

    else: 
        flash("Sucsessfully created a new camera!")
        return True
    return False
def setCameraCache():
    if session.get("isAdmin", False) == True: # IF THE USER IS ADMIN 
        session['cameraTable'] = selectFromDB(pathToDB, "camera", log=False) # SETS THE CASHE VARIABLE TO ALL OF THE CAMERA ROWS FROM THE CAMERA TABLE
    else:
        session['cameraTable'] = selectFromDB(pathToDB, "camera", ["WHERE"], ["adminView"], [False], log=False) # DOES THE SAME AS ABOVE BUT IT DOES NOT ADD THE ROWS THAT IS ONLY FOR THE ADMIN TO VIEW
                   


    


@views.route("/settings", methods=["GET", "POST"])
@login_required
def settings(): 

    if request.method == "POST":


# --- NEW USER HANDELING
        if request.form.get("createUser"): # IF A USER HAS CLICKED THE CREATE USER BUTTON
            email = request.form.get('email') # GETS THE INPUTTED EMAIL
            password = request.form.get('password') # GETS THE INPUTTED PASSWORD
            isAdmin = 'newUserCheckbox' in request.form # CHECKS IF THE MAKE ADMIN CHECKBOX IS CHECKED

            if checkEmailAndPassword(email, password) == True: # CHECKS IF THE INPUT INFORMATION IS VALID 
                user = User(email=email, password=generate_password_hash(password, method='sha256'), admin=isAdmin) # MAKES THE OBJECT WITH ALL OF THE DATA INPUTED
                db.session.add(user) # ADDS THE OBJECT TO THE SESSION, FOR ADDING TO THE DB
                db.session.commit() # COMMITS TO THE ACTION
                setCameraCache() # UPDATED THE CAMERA CACHE

# --- NEW CAMERA HANDELING  
        elif request.form.get("createCam"): # IF A USER HAS CLICKED THE ADD CAMERA BUTTON
            name = request.form.get('camName') # GETS THE CAMERA NAME
            ipAdress = request.form.get('camIpAdress') # GETS THE IP OF THE CAMERA INPUTTED
            adminView = 'newCamCheckbox' in request.form # GETS IF THE CHECKBOX HAS BEEN CHECKED
            
            if checkNameAndIp(name, ipAdress) == True: # CHECKS IF THE INPUT IS VALID
                camera = Camera(userId=current_user.id, name=name, ipAdress=ipAdress, adminView=adminView) # MAKES THE OBJECT WITH ALL OF THE DATA INPUTED
                db.session.add(camera) # ADDS THE OBJECT TO THE SESSION, FOR ADDING TO THE DB
                db.session.commit() # COMMITS TO THE ACTION
                setCameraCache() # UPDATES THE CACHE


# --- DELETE CAMERA HANDELING
        elif request.form.get("deleteCamId"): # IF SOMEONE PRESSED THE DELETE CAM BUTTON
            id = request.form.get("deleteCamId") # GETS THE ID OF THE BUTTON (SAME ID AS IN THE DATABACE)

            con = sqlite3.connect(pathToDB) # CONNECTS TO THE DB
            cursor = con.cursor() # SETS THE CURSOR
            cursor.execute("DELETE FROM 'camera' WHERE id=?", (id,)) # DELETES THE ROW THAT HAS BEEN PRESSED RELEASED ON
            con.commit() # COMMITS TO THE ACTION
        
            setCameraCache() # UPDATES THE CACHE
            flash(f"Sucsessfully deleted the Camera!") # Flashes a message






    return render_template("settings.html", user=current_user, isAdmin=session.get("isAdmin", False), cameraName=getNameAndAdminCamera(session.get("cameraTable", False)), cameraData=session.get("cameraTable", False))
