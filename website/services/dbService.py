




from flask import current_app
from flask import session


from ..models import Videos

from .. import logging
from .. import db

import sqlite3


def addVideo(app, userId, name, duration):
    with app.app_context(): # OPENS WITH APP CONTEXT TO ALLOW TO WRITE TO THE DB
        video_ = Videos(userId=userId, fileName=name, duration=duration) # ADDS THE VIDEO INTO THE DB
        db.session.add(video_) # ADDS THIS TO THE DB SESSION
        db.session.commit() # COMMITS THE ACTION




"""
___________________________________________ selectFromDB _________________________________________
This function reads data from a sqlite databace, it is dynamic in the sens that you could add an unlimteted parameters and unlimeded values to fit those parameters
The sqlite3 command is strored in the variable "getString"
dbPath = This is the path to the databace you want to read data from. example: "F:\Scripts\Python\canSat\website\instance\database.db" (str)
table = This is the name of the table you want to read data from. example: "flightmaster" (str)
columnList = This is the list of parameters you want to add to the "getString" variable. for example if you want to get data from column "id" then input ["id"]. If you want to inpuut and AND statment then add it in the lsit. For example if you want from the column id  where the loginId = 1 then input: ["id", "loginId"]. The value will be added under
valueList = This is the list of values you add to the column list.
argument = This is the argument you want to do, forexample could you add AND.
"""

def selectFromDB(dbPath, table, argumentList=None, columnList=None, valueList=None, log=True):
    def checkIfEmpty(data): 
        if data == []:
            return None
        return data
      
    con = sqlite3.connect(dbPath) # CONNECTS TO THE DB
    cursor = con.cursor() # MAKES THE CURSOR, FOR SELECTING THE DATA
    if argumentList != None and columnList != None and valueList != None: 

        getString = f"SELECT * FROM '{table}' {argumentList[0]} {columnList[0]}=?" # THIS IS THE STRING THAT IS GOING TO BE THE SQLITE COMMAND, ALREADY ADDED THE FIRST DATAPOINT
        if len(columnList) == len(valueList) or len(columnList) == 0 or len(valueList) == 0: # CHECKS IF THERE IS AN ERROR ON THE LENGTH OF THE INPUT PARAMETERS
            if len(columnList) >= 1: # IF THE INPUT PARAMETERS IS MORE THAN ONE, THEN IT ADDS THE AND SYNTAX AND THE PARAMETER TO THE GETSTRING VARIABLE
                for i, parameter in enumerate(columnList[1:]): # LOOPS OVER ALL OF THE EXTRA "AND" PARAMETERS
                    getString += f"{argumentList[i+1]} {parameter}=?"



                cursor.execute(getString, (valueList)) # SELECTS ALL OF THE DATA ACCORDING TO THE PARAMETERS GIVEN ABOVE
                data = cursor.fetchall() # FETCHES ALL OF THE DATA

                if log == True: # IF THE RESULTS SHULD BE LOGGED
                    logging.info(f"     Readed data from databace, command: {getString}{valueList}") # LOGS THE DATA
                    logging.debug(f"    data recived: {data}")

                return checkIfEmpty(data) # RETURNS ALL OF THE DATA


            cursor.execute(getString, (valueList[0],)) # SELECTS ALL OF THE GPS DATA, WE DO THIS TWICE BECAUSE THE SYNTAX OF THIS SUCS ;(, I NEED TI HAVE TRHE COMMA THERE WHAT A SHIT LIBARY
            data = cursor.fetchall() # FETCHES ALL OF THE DATA, GIVEN THE PARAMETERS ABOVE

            if log == True: # IF THE RESULTS SHULD BE LOGGED
                logging.info(f"     Databace command (read): {getString}{valueList}") # LOGS THE DATA
                logging.debug(f"    data recived: {data}")

            return checkIfEmpty(data) # RETURNS ALL OF THE DATA

        else: 
          raise Exception(f"Parameter error when reading from DB, there has to be a value for eatch parameter. Parameters: {columnList}, Values: {valueList}") # IF THERE WAS A ERROR OF THE LENGHT OF THE DATA
    else: 
        getString = f"SELECT * FROM '{table}'" # THIS IS THE STRING THAT IS GOING TO BE THE SQLITE COMMAND, ALREADY ADDED THE FIRST DATAPOINT
        cursor.execute(getString) # SELECTS ALL OF THE DATA ACCORDING TO THE PARAMETERS GIVEN ABOVE
        data = cursor.fetchall() # FETCHES ALL OF THE DATA

        if log == True: # IF THE RESULTS SHULD BE LOGGED
            logging.info(f"     Readed data from databace, command: {getString}{valueList}") # LOGS THE DATA
            logging.debug(f"    data recived: {data}")

        return checkIfEmpty(data)
