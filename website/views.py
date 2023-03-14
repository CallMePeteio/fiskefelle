from flask import Blueprint, render_template, request, flash, session
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash


from . import selectFromDB
from .models import User
from .models import Log
from . import pathToDB
from . import logging 
from . import db
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

        


        
    print(session["isAdmin"])
    return render_template("home.html", user=current_user, isAdmin=session["isAdmin"])





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
    


@views.route("/settings", methods=["GET", "POST"])
@login_required
def settings(): 

    if request.method == "POST":


# --- NEW USER HANDELING
        if request.form["createUser"]:
            email = request.form.get('email')
            password = request.form.get('password')
            isAdmin = 'checkbox' in request.form



            if checkEmailAndPassword(email, password) == True: 
                user = User(email=email, password=generate_password_hash(password, method='sha256'), admin=isAdmin)
                db.session.add(user)
                db.session.commit()





    return render_template("settings.html", user=current_user, isAdmin=session["isAdmin"])
