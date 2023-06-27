from flask import Blueprint, render_template, request, flash, session, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from .physical.rtsp import readRecStartVar

from . import getNameAndAdminCamera
from . import selectFromDB

from .models import FiskeFelle
from .models import Camera
from .models import User
from .models import Gate
from .models import Log


from . import maxRecordSizeGB
from . import getDirSize
from . import pathToDB
from . import logging 
from . import cache
#from . import relay
from . import db
import sqlite3
import json
import uuid
import time
import os




views = Blueprint('views', __name__) # MAKES THE BLUPRINT OBJECT


def logAction(userId, openDoor, turnLights): 
    log = Log(userId=userId, openDoor=openDoor, turnLights=turnLights)
    db.session.add(log)
    db.session.commit()
def getDefaultFiskefelle(): 
    
    defaultFiskefelle = selectFromDB(dbPath=pathToDB, table="fiskefelle")
    if defaultFiskefelle != None:
        return defaultFiskefelle[0]
    return None
def getDefaultIp(fiskefelleId):
    camIp = None
    camIp = selectFromDB(dbPath=pathToDB, table="camera", argumentList=["WHERE"], columnList=["fiskeFelleId"], valueList=str(fiskefelleId)) # GETS THE CAMERA IP 

    if camIp != None: 
        camIp = camIp[0][5]

    #####
    ### ADD SO IT SAYS THAT YOU NEED TO ADD A CAMERA
    
    return camIp


def setStartRecVar(var):
    instanceDir = os.path.abspath("instance") # GETS THE FULL PATH OF THE INSTANCE DIRECTORY
    recJsonPath = instanceDir + "/startRecord.json" # MAKES THE FULL PATH TO THE JOSN FILE
    startRec = {"startRec": var}
    session["startRec"] = var # STARTS RECORDING (CURRENTLY NOT USED)

    while True: # LOOPS A BUNCH OF TIMES BECAUSE THERE COULD BE OTHER SRIPTS READING/WRITING TO FILE CAUSING AN ERROR
        try:
            with open(recJsonPath, 'w') as outfile:
                json.dump(startRec, outfile)
                break
        except:
            print("There was an error acsessing: startRecord.json file!")




@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
     

    page_cam_ips = cache.get('page_cam_ips') or {} # MAKES THE CAM IPS DICTIONARY IF IT HASNT BEEN MADE YET
    pageDefaultFiskefelle = cache.get('pageDefaultFiskefelle') or {} # MAKES THE CAM pageDefaultFiskefelle DICTIONARY IF IT HASNT BEEN MADE YET

    page_uuid = request.form.get('page_uuid', request.args.get('page_uuid', str(uuid.uuid4()))) # GETS THE UNIQUE UUID CODE FROM A PREVIOUS REQUEST, IF THE CODE HASNT BEEN MADE BEFORE THAN MAKE A NEW 
    camIp = page_cam_ips.get(page_uuid) # GETS THE IP ADRESS OF THE CAMERA FROM THE UNIQUE UUID IF IT IS THE FIRST TIME MAKING A UUID REQEST THEN THIS RETURNS NONE
    fiskefelleId = pageDefaultFiskefelle.get(page_uuid) # GETS THE ID OF THE DEFAULT FISKEFELLE FROM THE UNIQUE UUID IF IT IS THE FIRST TIME MAKING A UUID REQEST THEN THIS RETURNS NONE

    if camIp == None or fiskefelleId == None: # IF THE "page_cam_ips.get(page_uuid)" RETURNS NONE OR THE pageDefaultFiskefelle.get(page_uuid) RETURNS NONE
        fiskefelleId = getDefaultFiskefelle()
        if fiskefelleId != None: # IF THERE HAS BEEN CREATED ANY FISKEFELLER BEFORE
            fiskefelleId = fiskefelleId[0]
            camIp = getDefaultIp(fiskefelleId) # GET A DEFAULT IP (FIRST TIME OPENING THE PAGE)

            page_cam_ips[page_uuid] = camIp # SETS THE UNIQUE IDENTIFYER
            
            pageDefaultFiskefelle[page_uuid] = fiskefelleId # SETS THE UNIQUE IDENTIFYER

    

    if request.method == "POST": 


#------------------------------- GATES
        if request.form.get("open"): # IF SOMEONE CLICS A BUTTON THAT IS SUPPOSED TO OPEN A GATE
            relayChannel = int(request.form.get("open")) -1 # GETS WHAT RELAY CHANNEL TO OPEN
            #relay.updateRelayState(1, relayChannel) # UPDATES THE RELAY HAT, CHANGES THE WANTED RELAY TO 1 (high)

            flash(f"Sucsessfully opened the Gate on channel: {relayChannel+1}", category="sucsess")
            logging.info(f"   Opened relay channel: {relayChannel +1}") # LOGS THE ACTION

        elif request.form.get("close"): # IF SOMEONE CLICS A BUTTON THAT IS SUPPOSED TO OPEN A GATE
            relayChannel = int(request.form.get("close")) -1 # GETS WHAT RELAY CHANNEL TO OPEN
            #relay.updateRelayState(0, relayChannel) # UPDATES THE RELAY HAT, CHANGES THE WANTED RELAY TO + (low)
            
            flash(f"Sucsessfully Closed the Gate on channel: {relayChannel+1}", category="sucsess")
            logging.info(f"   Closed relay channel: {relayChannel +1}") # LOGS THE ACTION



#------------------------------- CAMERA SWITCH
        elif request.form.get("fiskefelleId"): # IF SOMEONE WANTS TO CHANGE THE FISKEFELLE
            fiskefelleId = int(request.form.get("fiskefelleId")) # GETS THE FISKEFELLE ID
            pageDefaultFiskefelle[page_uuid] = fiskefelleId # SETS THE UNIQUE IDENTIFYER
            camIp = getDefaultIp(fiskefelleId) # GETS THE DEFAULT CAMERA IP, ACCORDING TO THE NEW FISKEFELLE ID
            page_cam_ips[page_uuid] = camIp # UPDATES THE CAMERA UUID.
            logging.info(f"     Showing camera with ip: {camIp}") # LOGS THE ACTION
            
        elif request.form.get("camera"): # IF SOMEONE WANTS TO CHANGE THE CAMERA
            camId = request.form.get("camera") # GETS THE ID OF THE CAMERA THEY WANT TO CHANGE TO
            camRow = selectFromDB(dbPath=pathToDB, table="camera", argumentList=["WHERE"], columnList=["id"], valueList=camId) # GETS THE ROW OF THE CAMERA THEY WANT TO VIEW
            camIp = camRow[0][5] # FINDS THE IP
            page_cam_ips[page_uuid] = camIp # UPDATES THE UUID LINK
            logging.info(f"     Showing camera with id: {camRow[0][0]}") # LOGS THE ACTION


        
#------------------------------- RECORDING

# NOTE NEED TO MAKE SO THAT EATCH RECORDING IS INDEPENDENT TO EATCH USER
        elif request.form.get("startRecording"):
            recDir = os.path.abspath("website/recordings") # FINDS THE FULL PATH TO THE RECORDING DIR
            recDirSize = getDirSize(recDir) # GETS THE SIZE OF ALL OF THE ITEMS IN THE DIRECTORY IN GB
            
            if recDirSize <= maxRecordSizeGB:
                setStartRecVar(True) # STARTS RECORDING (video.py)
            else:
                setStartRecVar(True)
                
                flash(f"There is not enough space to start another video, used size: {recDirSize}gb/{maxRecordSizeGB}gb", category='error')
            
        elif request.form.get("stopRecording"):

            setStartRecVar(False)
            time.sleep(0.5)
                   

        


    cache.set('page_cam_ips', page_cam_ips)
    cache.set('pageDefaultFiskefelle', pageDefaultFiskefelle)

    session["selectedCamIp"] = camIp
    selectedCamera = selectFromDB(dbPath=pathToDB, table="camera", argumentList=["WHERE"], columnList=["ipAdress"], valueList=[session["selectedCamIp"]])
    if selectedCamera != None:
        isRtsp=selectedCamera[0][3]
    else:
        isRtsp = None



    return render_template("home.html", user=current_user, isAdmin=session.get("isAdmin", False), cameraName=getNameAndAdminCamera(session.get("cameraTable", False)), cameraData=session.get("cameraTable", False), camIp=camIp, fiskefelleId=fiskefelleId, page_uuid=page_uuid, fiskefelleData=session.get("fiskefelleTable", False), gateData=session.get("gateTable", False), isRtsp=isRtsp, is_recording=readRecStartVar())





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
    session['cameraTable'] = selectFromDB(pathToDB, "camera", log=False) # SETS THE CASHE VARIABLE TO ALL OF THE CAMERA ROWS FROM THE CAMERA TABLE
def setFiskefelleCache(): 
    session['fiskefelleTable'] = selectFromDB(pathToDB, "fiskefelle", log=False) # SETS THE CASHE VARIABLE TO ALL OF THE CAMERA ROWS FROM THE CAMERA TABLE
def setGateCache(): 
    session["gateTable"] = selectFromDB(pathToDB, "gate", log=False)            
def setUserCache(): 
    session["userTable"] = selectFromDB(pathToDB, "user", log=False) # UPDATES THE USER CACHE
    
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
                setUserCache() # UPDATES THE USER CACHE

        elif request.form.get("deleteUser"): 
            userId = request.form.get("deleteUser")
            
            if checkValidDeleteId(userId) == True: 
                con = sqlite3.connect(pathToDB) # CONNECTS TO THE DB
                cursor = con.cursor() # SETS THE CURSOR
                cursor.execute("DELETE FROM 'user' WHERE id=?", (userId,)) # DELETES THE ROW THAT HAS BEEN PRESSED RELEASED ON
                con.commit() # COMMITS TO THE ACTION
                con.close()

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
                camera = Camera(userId=current_user.id, fiskeFelleId=fiskefelleId, rstp=isRstp, name=name, ipAdress=ipAdress) # MAKES THE OBJECT WITH ALL OF THE DATA INPUTED
                db.session.add(camera) # ADDS THE OBJECT TO THE SESSION, FOR ADDING TO THE DB
                db.session.commit() # COMMITS TO THE ACTION
                setCameraCache() # UPDATES THE CACHE

# --- DELETE CAMERA HANDELING
        elif request.form.get("deleteCamId"): # IF SOMEONE PRESSED THE DELETE CAM BUTTON
            camId = request.form.get("deleteCamId") # GETS THE ID OF THE BUTTON (SAME ID AS IN THE DATABACE)

            con = sqlite3.connect(pathToDB) # CONNECTS TO THE DB
            cursor = con.cursor() # SETS THE CURSOR
            cursor.execute("DELETE FROM 'camera' WHERE id=?", (camId,)) # DELETES THE ROW THAT HAS BEEN PRESSED RELEASED ON
            con.commit() # COMMITS TO THE ACTION
            con.close()
        
            setCameraCache() # UPDATES THE CACHE
            flash(f"Sucsessfully deleted the Camera!") # Flashes a message





# --- CREATE GATE HANDELING
        elif request.form.get("createGate"):
            fiskefelleId = request.form.get("fiskefelleType") # GETS THE ID OF THE FISKEFELLE THAT THE CAMERA SHULD BE TIED TO
            gateName = request.form.get("gateName") # GETS THE NAME OF THE GATE, FORM THE INPUT FIELD
            relayChannel = request.form.get("gateRelayChannel") # GETS WHAT RELAY CHANNEL THE BUTTON SHULD SWITCH

            if checkNameRelayChannel(gateName, relayChannel, fiskefelleId) == True: # CHECKS IF THERE ISNT ANYTHING WRONG WITH THE INPUT
                gate = Gate(userId=current_user.id, fiskeFelleId=fiskefelleId, name=gateName, relayChannel=relayChannel) # MAKES THE GATE OBJECT
                db.session.add(gate) # ADDS THE GATE TO THE SESSION
                db.session.commit() # WRITES THE GATE TO THE DB
                setGateCache() # UPDATES THE CACHE

# --- DELETE GATE HANDELING
        elif request.form.get("deleteGateId"): # IF SOMEONE PRESSED THE DELETE CAM BUTTON
            gateId = request.form.get("deleteGateId") # GETS THE ID OF THE BUTTON (SAME ID AS IN THE DATABACE)

            con = sqlite3.connect(pathToDB) # CONNECTS TO THE DB
            cursor = con.cursor() # SETS THE CURSOR
            cursor.execute("DELETE FROM 'gate' WHERE id=?", (gateId,)) # DELETES THE ROW THAT HAS BEEN PRESSED RELEASED ON
            con.commit() # COMMITS TO THE ACTION
            con.close()
        
            setGateCache() # UPDATES THE CACHE
            flash(f"Sucsessfully deleted the Camera!") # Flashes a message




  
# --- CREATE FISKEFELLE HANELING
        elif request.form.get("createFiskefelle"):  # IF SOMEONE CLICKS THE "Create Fiskefelle" POST BUTTON
            name = request.form.get("nameFiskefelle") # GETS THE NAME OF THE FISKEFELLE

            if checkFiskefelleName(name) == True: # CHECKS IF THERE ISNT ANY INVALID INPUT IN THE FISKEFELLE INPUT BOX
                fiskefelle = FiskeFelle(userId=current_user.id, name=name) # MAKES THE FISKEFELLE OBJECT
                db.session.add(fiskefelle) # ADDS IT TO THE SESSION
                db.session.commit() # WRITES IT TO THE DB
                setFiskefelleCache() # UPDATES THE CACHE

# -- DELETE FISKEFELLE HANDELING
        elif request.form.get("deleteFiskefelleId"):
            fiskefelleId = request.form.get("deleteFiskefelleId") # GETS THE ID OF THE FISKELLE THAT WAS DELETED (trash can button)

            con = sqlite3.connect(pathToDB) # CONNECTS TO THE DB
            cursor = con.cursor() # SETS THE CURSOR
            cursor.execute("DELETE FROM 'fiskefelle' WHERE id=?", (fiskefelleId,)) # DELETES THE ROW THAT HAS BEEN PRESSED RELEASED ON
            cursor.execute("DELETE FROM 'camera' WHERE fiskeFelleid=?", (fiskefelleId,)) # DELEATS THE CAMERAS THAT HAS BEEN ATTATCHED TO THE FISKEFELLE
            cursor.execute("DELETE FROM 'gate' WHERE fiskeFelleid=?", (fiskefelleId,)) # DELEATS THE GATE THAT HAS BEEN ATTATCHED TO THE FISKEFELLE
            con.commit() # COMMITS TO THE ACTION
            con.close() # CLOSES THE CONNECTION
            setFiskefelleCache() # UPDATES THE CACHE
            setCameraCache() # UPDATES THE CACHE
            setGateCache() # UPDATES THE GATE CACHE
            flash(f"Sucsessfully deleted the Fiskefelle!") # Flashes a message




    #print()
    #print(session.get("cameraTable", False))
    #print(session.get("fiskefelleTable", False))
    #print(session.get("gateTable", False))
    #print(session.get("userTable", False))
    #print()

    if session.get("fiskefelleTable", False) != None: # IF THERE IS ANY DATA IN THE FISKEFELLE TABLE
        fiskefelleIdToName = {fiskefelle[0]: fiskefelle[2] for fiskefelle in session.get("fiskefelleTable", False)} # THIS REUTRNS A DICTIONARY THAT LOOKS LIKE THIS: {id: name, 1:"storelven", 2:"beiarelven"}
    else: 
        fiskefelleIdToName = None

    return render_template("settings.html", user=current_user, isAdmin=session.get("isAdmin", False), cameraName=getNameAndAdminCamera(session.get("cameraTable", False)), cameraData=session.get("cameraTable", False), fiskefelleData=session.get("fiskefelleTable", False), fiskefelleIdToName=fiskefelleIdToName, gateData=session.get("gateTable", False), userData=session.get("userTable", False))
