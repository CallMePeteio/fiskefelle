


from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from ..services.dbService import selectFromDB

from ..models import User

from .. import config
from .. import db 



auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST': # IF THE USER HAS CLICKED THE "login" BUTTON
        email = request.form.get('email') # GETS THE EMAIL FROM THE INPUT BOX 
        password = request.form.get('password') # GETS THE PASSWORD FROM THE INPUT BOX
        user = User.query.filter_by(email=email).first() # GETS IF THE USER EXISTS

        if user: # IF THE USER EXISTS 
            if check_password_hash(user.password, password): # CHECK IF THE PASSWORD IS CORRECT (unhases the password)
                flash('Logged in successfully!', category='success') # FLASHES THE INPUT MESSAGE
                login_user(user, remember=True) # LOGS IN THE USER

                isAdmin = selectFromDB(config.pathToDB, "user", ["WHERE"], ["id"], [current_user.id], log=True)
                if isAdmin[0][len(isAdmin[0]) -1] == 1:
                    session["isAdmin"] = True # SETS THE USER AS ADMIN
                else:
                    session["isAdmin"] = False # SETS THE USER AS USER

                camTable = selectFromDB(config.pathToDB, "camera", ["WHERE"], log=False) # GETS ALL OF THE ROWS FROM THE "camera" TABLE
                fiskefeleTable = selectFromDB(config.pathToDB, "fiskefelle", ["WHERE"], log=False) # GETS ALL OF THE ROWS FROM THE "camera" TABLE
                gateTable = selectFromDB(config.pathToDB, "gate", ["WHERE"], log=False)
                
                session["gateTable"] = gateTable  # SETS THE RECIVE DATA TO A GLOBAL VARIABLE, IM USING THIS TO CASH THE TABLE "gateTable", SO I DONT HAFT TO READ FORM THE DB EVRYTIME I MAKE A REQUEST
                session['cameraTable'] = camTable # SETS THE RECIVE DATA TO A GLOBAL VARIABLE, IM USING THIS TO CASH THE TABLE "cameras", SO I DONT HAFT TO READ FORM THE DB EVRYTIME I MAKE A REQUEST
                session["fiskefelleTable"] = fiskefeleTable # SETS THE RECIVE DATA TO A GLOBAL VARIABLE, IM USING THIS TO CASH THE TABLE "fiskefelle", SO I DONT HAFT TO READ FORM THE DB EVRYTIME I MAKE A REQUEST
                session["userTable"] = selectFromDB(config.pathToDB, "user", log=False) # UPDATES THE USER CACHE
                session["startRec"] = False # SETS THE DEFAULT VALUE IF YOU SHULD START RECORDING (DONT RECORD)
                
                return redirect("/") # REDIRECTS THE USER TO HOME

            else:
                flash('Incorrect password, try again.', category='error') # FLASHES THE INCORRECT PASSWORD MESSAGE 
        else:
            flash('Email does not exist.', category='error') # FLASHES THE EMAIL DOES NOT EXIST MESSAGE

    return render_template("login.html", user=current_user, isAdmin=False, cameraName=False) # RENDERS "login.html"


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/generateAdminUser', methods=["GET", "POST"])
def debug():
    user = User.query.filter_by(email=config.adminEmail).first() # GETS IF THE ADMIN EMAIL HAS ALREADY BEEN CREATED
    if not user: # IF THE USER HASNT BEEN CREATED BEFORE
        if request.method == "POST":
 
            adminPassword = request.form.get("password") # GETS THE PASSWORD INPUTTED BY THE SETUP TECH

            user = User(email=config.adminEmail, password=generate_password_hash(adminPassword, method='sha256'), admin=True) # MAKES THE USER, AND HASHES THE PASSWORD
            db.session.add(user)
            db.session.commit()

            user = User.query.filter_by(email=config.adminEmail).first() # MAKES THE USER OBJECT
            login_user(user, remember=True) # LOGS IN THE USER

            camTable = selectFromDB(config.pathToDB, "camera", ["WHERE"], log=False) # GETS ALL OF THE ROWS FROM THE "camera" TABLE
            fiskefeleTable = selectFromDB(config.pathToDB, "fiskefelle", ["WHERE"], log=False) # GETS ALL OF THE ROWS FROM THE "camera" TABLE
            gateTable = selectFromDB(config.pathToDB, "gate", ["WHERE"], log=False)
                
            session["gateTable"] = gateTable  # SETS THE RECIVE DATA TO A GLOBAL VARIABLE, IM USING THIS TO CASH THE TABLE "gateTable", SO I DONT HAFT TO READ FORM THE DB EVRYTIME I MAKE A REQUEST
            session['cameraTable'] = camTable # SETS THE RECIVE DATA TO A GLOBAL VARIABLE, IM USING THIS TO CASH THE TABLE "cameras", SO I DONT HAFT TO READ FORM THE DB EVRYTIME I MAKE A REQUEST
            session["fiskefelleTable"] = fiskefeleTable # SETS THE RECIVE DATA TO A GLOBAL VARIABLE, IM USING THIS TO CASH THE TABLE "fiskefelle", SO I DONT HAFT TO READ FORM THE DB EVRYTIME I MAKE A REQUEST
            session["userTable"] = selectFromDB(config.pathToDB, "user", log=False) # UPDATES THE USER CACHE
            session["startRec"] = False # SETS THE DEFAULT VALUE IF YOU SHULD START RECORDING (DONT RECORD)
            session["isAdmin"] = True 



            return redirect("/") # REDIRECTS THE USER TO HOME
        return render_template("adminGeneration.html", user=current_user, adminGmail=config.adminEmail)
    else:
        return "<h1> ERROR ADMIN USER HAS ALREADY BEEN GENERATED </h1> <a href='/login' class='display-4 text-danger font-weight-bold' style='font-size: 1.7rem;'>Return to the Login Page!</a>"

  







