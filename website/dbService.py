




from flask import current_app
from flask import session


from .models import Videos

from . import db





def addVideo(app, userId, name, duration):
    with app.app_context(): # OPENS WITH APP CONTEXT TO ALLOW TO WRITE TO THE DB
        video_ = Videos(userId=userId, fileName=name, duration=duration) # ADDS THE VIDEO INTO THE DB
        db.session.add(video_) # ADDS THIS TO THE DB SESSION
        db.session.commit() # COMMITS THE ACTION