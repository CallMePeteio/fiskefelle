




dbName = "database.db"
pathToDataStorage = "/home/pi/fiskefelle/instance/"
pathToDB = pathToDataStorage + dbName


#_____________________________________ RtspStream _____________________________________
rtspLink = "rtsp://admin:Troll2014@192.168.1.20:554"
recordingsFolder = "website/static/recordings"
videoTimeFormat = "%d-%m-%Y_%H:%M:%S"
resolution = (1280, 720)
maxRecordSizeGB = 200
framesPerSecond = 9
userId_ = 1





#________________________________________ Misc ________________________________________
"""
Level: NOTSET > DEBUG > INFO > WARNING > ERROR > CRITICAL
Value:   0    >  10   >  20  >    30   >  40   >  50
"""
adminEmail = "admin@gmail.com"
loggingLevel = 20
