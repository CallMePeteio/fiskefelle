from flask import Blueprint, render_template, request, flash, session, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from ..services.dbService import deleteRowColumn
from ..services.dbService import addRowToTable
from ..services.dbService import selectFromDB
from ..services.rtsp import getDirSize

from ..models import FiskeFelle
from ..models import Camera
from ..models import User
from ..models import Gate
from ..models import Log

from .. import config
from .. import logging 
from .. import cache
#from . import relay
from .. import app
from .. import db   
import sqlite3
import uuid
import time
import os




settings = Blueprint('settings', __name__) # MAKES THE BLUPRINT OBJECT



def checkFiskefelleName(name): 
    fiskefeller = FiskeFelle.query.filter_by(name=name).first()

    if fiskefeller:
        flash('Name already exists', category='error')
    elif name.find(" ") != -1: # IF THE NAME CONTAINS ANY SPACES
        flash('Name cant contain spaces', category='error') 
    elif len(name) <= 3: 
        flash("Name must contain more than 3 characters", category='error')
    elif len(name) > 150: # IF THE NAME IS TO LONG
        flash('Max charachter lenght is 150 characters', category='error')
    else: 
        flash("Created new fiskefelle")
        return True # RETURNS TRUE IF THE NAME FORFILLS ALL OF THE REQUIRMENTS
    return False # RETURNS FALSE OF THE NAME DOSENT FORFILL ALL OF THE REQUIRMENTS
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
def checkNameIpId(name, ip, fiskefelleId): 

    if len(name) > 130: 
        flash("Name cant be greater than 130 charachters", category='error')
    elif fiskefelleId == "None":
        flash(f"You need to make fiskefelle before you make camera!", category='error')
    elif Camera.query.filter_by(ipAdress=ip).first():
        flash(f"You cant have the same ip adress for two diffrent cameras", category="error")
    else: 
        flash("Sucsessfully created a new camera!")
        return True
    return False
def checkNameRelayChannel(name, relayChannel, fiskefelleId):
    gateTable = session.get("gateTable", False) # GETS THE CACHED GATE TABLES

    if gateTable != None and gateTable != False: # IF ANY DATA EXISTS
        for gate in gateTable: # LOOPS OVER ALL OF THE GATES
                
                print(gate[3], name)
                print(gate[2], fiskefelleId)
            
                if int(relayChannel) == gate[4]: # IF THE RELAYCHANNEL IS ALREADY IN USE
                    flash(f"Relay channel {relayChannel} is already in use by: {gate[3]}", category="error")
                    return False # RETURNS FALSE TO STOP THE PROGRAM TO WRITING TO THE DB
                
                if name == gate[3] and gate[2] == int(fiskefelleId): # IF IT IS THE FISKEFELLE WE ARE ADDING A GATE TO: # IF THE NAME IS ALREADY IN USE
                    flash(f"Name: {name} already in Exists!", category="error") # FLASHES THE ERROR ON SCREEN
                    return False # RETURNS FALSE TO STOP THE PROGRAM TO WRITING TO THE DB

    if fiskefelleId == "None":
        flash(f"You need to make fiskefelle before you make camera!", category='error') 
    elif len(name) >= 130: 
        flash("The name cannot be greater than 130 characters", category="error")
    elif len(name) < 3: 
        flash("The name cannot be less than 3 characters", category="error")
    else: 
        flash("Sucsessfully created a new Gate!", category="sucsess")
        return True
    return False # RETURNS FALSE TO STOP THE PROGRAM TO WRITING TO THE DB
def checkValidDeleteId(id):
    userData = session.get("userTable", False)

    for user in userData: 
        if user[0] == int(id): 
            if user[1] != "admin@gmail.com": 
                return True
            else: 
                flash("You Cheecky bugger, Cannot delete the admin user", category="error")
    flash("Error on finding the correct user to delete", category="error")
    return False     


def setCameraCache():
    session['cameraTable'] = selectFromDB(config.pathToDB, "camera", log=False) # SETS THE CASHE VARIABLE TO ALL OF THE CAMERA ROWS FROM THE CAMERA TABLE
def setFiskefelleCache(): 
    session['fiskefelleTable'] = selectFromDB(config.pathToDB, "fiskefelle", log=False) # SETS THE CASHE VARIABLE TO ALL OF THE CAMERA ROWS FROM THE CAMERA TABLE
def setGateCache(): 
    session["gateTable"] = selectFromDB(config.pathToDB, "gate", log=False)            
def setUserCache(): 
    session["userTable"] = selectFromDB(config.pathToDB, "user", log=False) # UPDATES THE USER CACHE
    
@settings.route("/settings", methods=["GET", "POST"])
@login_required
def settings_(): 

    if request.method == "POST":


# --- NEW USER HANDELING
        if request.form.get("createUser"): # IF A USER HAS CLICKED THE CREATE USER BUTTON
            email = request.form.get('email') # GETS THE INPUTTED EMAIL
            password = request.form.get('password') # GETS THE INPUTTED PASSWORD
            isAdmin = 'newUserCheckbox' in request.form # CHECKS IF THE MAKE ADMIN CHECKBOX IS CHECKED

            if checkEmailAndPassword(email, password) == True: # CHECKS IF THE INPUT INFORMATION IS VALID 
                addRowToTable(User, {"email": email, "password": generate_password_hash(password, method='scrypt'), "admin": isAdmin}, app)
                setUserCache() # UPDATES THE USER CACHE

        elif request.form.get("deleteUser"): 
            userId = request.form.get("deleteUser")
            
            if checkValidDeleteId(userId) == True: 
                deleteRowColumn(User, "id", userId) # DELETS THE CAMERA
                setUserCache()  # UPDATES THE CACHE
                flash(f"Sucsessfully deleted the User!") # Flashes a message




# --- NEW CAMERA HANDELING  
        elif request.form.get("createCam"): # IF A USER HAS CLICKED THE ADD CAMERA BUTTON
            name = request.form.get('camName') # GETS THE CAMERA NAME
            ipAdress = request.form.get('camIpAdress') # GETS THE IP OF THE CAMERA INPUTTED
            adminView = 'newCamCheckbox' in request.form # GETS IF THE CHECKBOX HAS BEEN CHECKED
            fiskefelleId = request.form.get("fiskefelleType") # GETS THE ID OF TsHE FISKEFELLE THAT THE CAMERA SHULD BE TIED TO

            if request.form.get("streamOption") == "rstp": # CHECKS IF THE RSTP BUTTON WAS CHECKED
                isRstp = True
            else:
                isRstp = False
            
            if checkNameIpId(name, ipAdress, fiskefelleId) == True: # CHECKS IF THE INPUT IS VALID
                addRowToTable(Camera, {"userId": current_user.id, "fiskeFelleId": fiskefelleId, "rstp": isRstp, "name": name, "ipAdress": ipAdress}, app)
                setCameraCache() # UPDATES THE CACHE

# --- DELETE CAMERA HANDELING
        elif request.form.get("deleteCamId"): # IF SOMEONE PRESSED THE DELETE CAM BUTTON
            camId = request.form.get("deleteCamId") # GETS THE ID OF THE BUTTON (SAME ID AS IN THE DATABACE)
            deleteRowColumn(Camera, "id", camId) # DELETS THE CAMERA
            setCameraCache() # UPDATES THE CACHE
            flash(f"Sucsessfully deleted the Camera!") # Flashes a message




# --- CREATE GATE HANDELING
        elif request.form.get("createGate"):
            fiskefelleId = request.form.get("fiskefelleType") # GETS THE ID OF THE FISKEFELLE THAT THE CAMERA SHULD BE TIED TO
            gateName = request.form.get("gateName") # GETS THE NAME OF THE GATE, FORM THE INPUT FIELD
            relayChannel = request.form.get("gateRelayChannel") # GETS WHAT RELAY CHANNEL THE BUTTON SHULD SWITCH

            if checkNameRelayChannel(gateName, relayChannel, fiskefelleId) == True: # CHECKS IF THERE ISNT ANYTHING WRONG WITH THE INPUT
                addRowToTable(Gate, {"userId": current_user.id, "fiskeFelleId": fiskefelleId, "name": gateName, "relayChannel": relayChannel}, app)
                setGateCache() # UPDATES THE CACHE

# --- DELETE GATE HANDELING
        elif request.form.get("deleteGateId"): # IF SOMEONE PRESSED THE DELETE CAM BUTTON
            gateId = request.form.get("deleteGateId") # GETS THE ID OF THE BUTTON (SAME ID AS IN THE DATABACE)
            deleteRowColumn(Gate, "id", gateId) # DELETS THE GATE
            setGateCache() # UPDATES THE CACHE
            flash(f"Sucsessfully deleted the Camera!") # Flashes a message




  
# --- CREATE FISKEFELLE HANELING
        elif request.form.get("createFiskefelle"):  # IF SOMEONE CLICKS THE "Create Fiskefelle" POST BUTTON
            name = request.form.get("nameFiskefelle") # GETS THE NAME OF THE FISKEFELLE

            if checkFiskefelleName(name) == True: # CHECKS IF THERE ISNT ANY INVALID INPUT IN THE FISKEFELLE INPUT BOX
                addRowToTable(FiskeFelle, {"userId": current_user.id, "name": name}, app)
                setFiskefelleCache() # UPDATES THE CACHE
                

# -- DELETE FISKEFELLE HANDELING
        elif request.form.get("deleteFiskefelleId"):
            fiskefelleId = request.form.get("deleteFiskefelleId") # GETS THE ID OF THE FISKELLE THAT WAS DELETED (trash can button)

            deleteRowColumn(FiskeFelle, "id", fiskefelleId)
            deleteRowColumn(Camera, "fiskeFelleId", fiskefelleId)
            deleteRowColumn(Gate, "fiskeFelleId", fiskefelleId)

            setFiskefelleCache() # UPDATES THE CACHE
            setCameraCache() # UPDATES THE CACHE
            setGateCache() # UPDATES THE GATE CACHE
            flash(f"Sucsessfully deleted the Fiskefelle!") # Flashes a message



    if session.get("fiskefelleTable", False) != None: # IF THERE IS ANY DATA IN THE FISKEFELLE TABLE
        fiskefelleIdToName = {fiskefelle[0]: fiskefelle[2] for fiskefelle in session.get("fiskefelleTable", False)} # THIS REUTRNS A DICTIONARY THAT LOOKS LIKE THIS: {id: name, 1:"storelven", 2:"beiarelven"}
    else: 
        fiskefelleIdToName = None

    return render_template("settings.html", user=current_user, isAdmin=session.get("isAdmin", False), cameraData=session.get("cameraTable", False), fiskefelleData=session.get("fiskefelleTable", False), fiskefelleIdToName=fiskefelleIdToName, gateData=session.get("gateTable", False), userData=session.get("userTable", False))
   