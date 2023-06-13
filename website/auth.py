


from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import selectFromDB
from .models import User
from . import pathToDB
from . import db 



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

                isAdmin = selectFromDB(pathToDB, "user", ["WHERE"], ["id"], [current_user.id], log=True)
                if isAdmin[0][len(isAdmin[0]) -1] == 1:
                    session["isAdmin"] = True # SETS THE USER AS ADMIN
                else:
                    session["isAdmin"] = False # SETS THE USER AS USER

                camTable = selectFromDB(pathToDB, "camera", ["WHERE"], log=False) # GETS ALL OF THE ROWS FROM THE "camera" TABLE
                fiskefeleTable = selectFromDB(pathToDB, "fiskefelle", ["WHERE"], log=False) # GETS ALL OF THE ROWS FROM THE "camera" TABLE
                gateTable = selectFromDB(pathToDB, "gate", ["WHERE"], log=False)
                
                session["gateTable"] = gateTable  # SETS THE RECIVE DATA TO A GLOBAL VARIABLE, IM USING THIS TO CASH THE TABLE "gateTable", SO I DONT HAFT TO READ FORM THE DB EVRYTIME I MAKE A REQUEST
                session['cameraTable'] = camTable # SETS THE RECIVE DATA TO A GLOBAL VARIABLE, IM USING THIS TO CASH THE TABLE "cameras", SO I DONT HAFT TO READ FORM THE DB EVRYTIME I MAKE A REQUEST
                session["fiskefelleTable"] = fiskefeleTable # SETS THE RECIVE DATA TO A GLOBAL VARIABLE, IM USING THIS TO CASH THE TABLE "fiskefelle", SO I DONT HAFT TO READ FORM THE DB EVRYTIME I MAKE A REQUEST
                session["userTable"] = selectFromDB(pathToDB, "user", log=False) # UPDATES THE USER CACHE
                
                return redirect(url_for('views.home')) # REDIRECTS THE USER TO HOME

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
    adminEmail = "admin@gmail.com" # DEFINES THE DEFAULT ADMIN USERNAME   

    user = User.query.filter_by(email=adminEmail).first() # GETS IF THE ADMIN EMAIL HAS ALREADY BEEN CREATED
    if not user: # IF THE USER HASNT BEEN CREATED BEFORE
        if request.method == "POST":
 
            adminPassword = request.form.get("password") # GETS THE PASSWORD INPUTTED BY THE SETUP TECH

            user = User(email=adminEmail, password=generate_password_hash(adminPassword, method='sha256'), admin=True) # MAKES THE USER, AND HASHES THE PASSWORD
            db.session.add(user)
            db.session.commit()

            user = User.query.filter_by(email=adminEmail).first() # MAKES THE USER OBJECT
            login_user(user, remember=True) # LOGS IN THE USER
            return redirect(url_for('views.home')) # REDIRECTS THE USER TO HOME
        return render_template("adminGeneration.html", user=current_user)
    else:
        return "<h1> ERROR ADMIN USER HAS ALREADY BEEN GENERATED </h1> <a href='/login' class='display-4 text-danger font-weight-bold' style='font-size: 1.7rem;'>Return to the Login Page!</a>"

  











#@auth.route('/sign-up', methods=['GET', 'POST'])
#def sign_up():
#    if request.method == 'POST':
#        email = request.form.get('email')
#        first_name = request.form.get('firstName')
#        password1 = request.form.get('password1')
#        password2 = request.form.get('password2')
#
#        user = User.query.filter_by(email=email).first()
#        if user:
#            flash('Email already exists.', category='error')
#        elif len(email) < 4:
#            flash('Email must be greater than 3 characters.', category='error')
#        elif len(first_name) < 2:
#            flash('First name must be greater than 1 character.', category='error')
#        elif password1 != password2:
#            flash('Passwords don\'t match.', category='error')
#        elif len(password1) < 7:
#            flash('Password must be at least 7 characters.', category='error')
#        else:
#            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
#                password1, method='sha256'))
#            db.session.add(new_user)
#            db.session.commit()
#            login_user(new_user, remember=True)
#            flash('Account created!', category='success')
#            return redirect(url_for('views.home'))
#
#    return render_template("sign_up.html", user=current_user)
#