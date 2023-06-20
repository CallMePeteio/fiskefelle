from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func




class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    admin = db.Column(db.Boolean)


class FiskeFelle(db.Model):
    __tablename__ = 'fiskefelle'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(150))
    adminView = db.Column(db.Boolean)

class Videos(db.Model):
    __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    fileName = db.Column(db.String(150))
    duration = db.Column(db.String(150))



class Camera(db.Model): 
    __tablename__ = 'camera'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    fiskeFelleId = db.Column(db.Integer, db.ForeignKey('fiskefelle.id'))
    rstp = db.Column(db.Boolean)
    name = db.Column(db.String(150))
    ipAdress = db.Column(db.String(150))


class Gate(db.Model): 
    __tablename__ = 'gate'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    fiskeFelleId = db.Column(db.Integer, db.ForeignKey('fiskefelle.id'))
    name = db.Column(db.String(150))
    relayChannel = db.Column(db.Integer)


class Log(db.Model): 
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime(timezone=True), default=func.now())

    openDoor = db.Column(db.Boolean)
    turnLights = db.Column(db.Boolean)




