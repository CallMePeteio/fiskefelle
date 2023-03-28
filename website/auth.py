


from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import maxLoginAtemts
from . import selectFromDB
from . import timeoutMin
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
                    camTable = selectFromDB(pathToDB, "camera", ["WHERE"], log=False) # GETS ALL OF THE ROWS FROM THE "camera" TABLE
                    session["isAdmin"] = True # SETS THE USER AS ADMIN
                    session['cameraTable'] = camTable # SETS THE RECIVE DATA TO A GLOBAL VARIABLE, IM USING THIS TO CASH THE TABLE "cameras", SO I DONT HAFT TO READ FORM THE DB EVRYTIME I MAKE A REQUEST
                
                else:
                    camTableNotAdmin = selectFromDB(pathToDB, "camera", ["WHERE"], ["adminView"], [False], log=True) # GETS THE CAM TABLE, THAT NONADMIN USERS CAN VIEW 
                    session["isAdmin"] = False
                    session['cameraTable'] = camTableNotAdmin # SETS THE RECIVE DATA TO A GLOBAL VARIABLE, IM USING THIS TO CASH THE TABLE "cameras", SO I DONT HAFT TO READ FORM THE DB EVRYTIME I MAKE A REQUEST
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


@auth.route('/debug')
def debug():

    loginEmail = "admin@gmail.com" # ALLE DE FORKJELLIGE BRUKERNAVNENE PÅ NETTSIDENM
    loginPaswd = "Passord1" # ALLE DE FORKJELLIGE PASSORDENE TIL NETTSIDENE

    user = User(email=loginEmail, password=generate_password_hash(loginPaswd, method='sha256'), admin=True)
    db.session.add(user)
    db.session.commit()


    return render_template("base.html", user=current_user)

  











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