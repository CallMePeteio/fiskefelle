

from flask_login import login_required
from flask_login import current_user

from flask import render_template
from flask import current_app
from flask import Blueprint
from flask import request
from flask import session

from ..services.dbService import selectFromDB
from ..services.rtsp import getDirSize

from .. import logging 
from .. import config
from .. import cache
from .. import db

import json
import uuid
import time
import os 


def logAction(userId, openDoor, turnLights): 
    log = Log(userId=userId, openDoor=openDoor, turnLights=turnLights)
    db.session.add(log)
    db.session.commit()
def getDefaultFiskefelle(): 
    
    defaultFiskefelle = selectFromDB(dbPath=config.pathToDB, table="fiskefelle")
    if defaultFiskefelle != None:
        return defaultFiskefelle[0]
    return None
def getDefaultIp(fiskefelleId):
    camIp = None
    camIp = selectFromDB(dbPath=config.pathToDB, table="camera", argumentList=["WHERE"], columnList=["fiskeFelleId"], valueList=str(fiskefelleId)) # GETS THE CAMERA IP 

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




home = Blueprint('home', __name__) # MAKES THE BLUPRINT OBJECT

@home.route('/', methods=['GET', 'POST'])
@login_required
def home_():
     

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
            camRow = selectFromDB(dbPath=config.pathToDB, table="camera", argumentList=["WHERE"], columnList=["id"], valueList=camId) # GETS THE ROW OF THE CAMERA THEY WANT TO VIEW
            camIp = camRow[0][5] # FINDS THE IP
            page_cam_ips[page_uuid] = camIp # UPDATES THE UUID LINK
            logging.info(f"     Showing camera with id: {camRow[0][0]}") # LOGS THE ACTION


        
#------------------------------- RECORDING

# NOTE NEED TO MAKE SO THAT EATCH RECORDING IS INDEPENDENT TO EATCH USER
        elif request.form.get("startRecording"):
            recDir = os.path.abspath("website/recordings") # FINDS THE FULL PATH TO THE RECORDING DIR
            recDirSize = getDirSize(recDir) # GETS THE SIZE OF ALL OF THE ITEMS IN THE DIRECTORY IN GB
            
            if recDirSize <= config.maxRecordSizeGB:
                current_app.stream.startRecoring = True
            else:
                current_app.stream.startRecoring = False
                
                flash(f"There is not enough space to start another video, used size: {recDirSize}gb/{config.maxRecordSizeGB}gb", category='error')
            
        elif request.form.get("stopRecording"):
            current_app.stream.startRecoring = False
                   

    cache.set('page_cam_ips', page_cam_ips)
    cache.set('pageDefaultFiskefelle', pageDefaultFiskefelle)

    session["selectedCamIp"] = camIp
    selectedCamera = selectFromDB(dbPath=config.pathToDB, table="camera", argumentList=["WHERE"], columnList=["ipAdress"], valueList=[session["selectedCamIp"]])
    if selectedCamera != None:
        isRtsp=selectedCamera[0][3]
    else:
        isRtsp = None


   
    return render_template("home.html", user=current_user, isAdmin=session.get("isAdmin", False), cameraData=session.get("cameraTable", False), camIp=camIp, fiskefelleId=fiskefelleId, page_uuid=page_uuid, fiskefelleData=session.get("fiskefelleTable", False), gateData=session.get("gateTable", False), isRtsp=isRtsp, is_recording=current_app.stream.startRecoring)

