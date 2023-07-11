

"""
___________________________________ convertSecToHMS ___________________________________
This function converts seconds to HR:MIN:SEC format

Seconds = This is the amout of seconds you want to change to H:M:S format

"""
def convertSecToHMS(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))



"""
___________________________________ convertHMSToSec ___________________________________
This function converts HMS to minutes.

timeStr = This is the HMS time that you want to conver to minutes NOTE must be seperated by : (str)
"""

def convertHMSToSec(timeStr):
    hour, min, sec = map(int, timeStr.split(":"))
    return hour * 60 + min + sec/60



"""
____________________________________ transformList ____________________________________
This function takes input form the "videos" table, and transforms the list into a corecct
format, so it can easly be displayed. Used forexample in /blueprints/video.py

example input:
[(3, 1, '12-07-2023_08:19:13', '00:15:00'), (4, 1, '12-07-2023_08:20:13', '00:10:00'), (5, 1, '13-07-2023_08:19:13', '00:30:00')]

will return (two lists) :
[[(3, 1, '12-07-2023_08:19:13', '00:15:00'), (4, 1, '12-07-2023_08:20:13', '00:10:00')], (5, 1, '13-07-2023_08:19:13', '00:25:00')]
[(30.0, 2), (25.0, 1)]

The first list nests a list where they are the same day
the second list is the lenght and the amount of videos.

Returns None if videoItems is none or the length of videoItems is less than 1 
"""
def transformList(videoItems):

    if videoItems != None and len(videoItems) >= 1:

        dayVidLen, dayAmountVid = 0, 0
        finishedList, workingList, numLengthList = [], [], []
        dateSelector = videoItems[0][2].split("-")[0] # FINDS THE FIRST ITEMS DATE

        for video in videoItems:
            date = video[2].split("-")[0] # FINDS THE VIDEOITEMS DATE

            if date == dateSelector: 
                workingList.append(video)
            else:
                numLengthList.append((round(dayVidLen, 1), dayAmountVid))
                finishedList.append(workingList.copy())
                workingList.clear()
                
                workingList.append(video)
                dateSelector = date
                dayVidLen = 0
                dayAmountVid = 0

            dayAmountVid += 1
            videoTime = video[3]
            dayVidLen += convertHMSToSec(videoTime)

        finishedList.append(workingList.copy())
        numLengthList.append((round(dayVidLen, 1), dayAmountVid))

        return finishedList, numLengthList
    
    else:
        return None, None
