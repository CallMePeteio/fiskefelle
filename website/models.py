from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func




class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    admin = db.Column(db.Boolean)



class Log(db.Model): 
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime(timezone=True), default=func.now())

    openDoor = db.Column(db.Boolean)
    turnLights = db.Column(db.Boolean)




