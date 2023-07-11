



from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from flask import current_app
from flask import session


from ..models import Videos

from .. import logging
from .. import db

import sqlite3




"""
__________________________________________ deleteRowColumn ________________________________________
This function is used to delete a row from a certian table

Model = This is the class(model) that you want to add a row to 
columnName = This is the name of the column you want to delete, forexample if you want to delete somehting with the id of one, then input "id"
value = This is the value of what you want to delete, orexample if you want to delete somehting with the value of 1 then input 1
"""

def deleteRowColumn(Model, columnName, value):

   
    model_attrs = inspect(Model).attrs  # Inspect the model to get its attributes
    column_names = [] # Create an empty list to store column names

    for attr in model_attrs: # Loop over the attributes and add the keys (i.e., column names) to the list
        column_names.append(attr.key)

    
    if columnName not in column_names: # Check if the provided column name is in the list of column names for the model
        logging.critical(f"   Column {columnName} does not exist in table: {Model.__name__}!")
        return

    filter_condition = {columnName: value} # Use a dictionary to construct the filter condition
    numDeleted = Model.query.filter_by(**filter_condition).delete() # Delete the rows that match the filter condition
    db.session.commit() # Commit the changes to the database

    
    if numDeleted == 0: # Log a warning if no rows were deleted
        logging.warning(f"   No rows found to delete in table: {Model.__name__} with {columnName}: {value}")



"""
___________________________________________ addRowToTable ________________________________________
This function is used to add a row to a desiered table 

Model = This is the class(model) that you want to add a row to 
columnValues = This is the values of the colums, in dictionary form, forexample:
{"userId": current_user.id, "fiskeFelleId": fiskefelleId, "rstp": isRstp, "name": name, "ipAdress": ipAdress}
"""

def addRowToTable(Model, columnValues, app):
    with app.app_context():
        try:
            newRecord = Model(**columnValues)
            db.session.add(newRecord)
            db.session.commit()
        except Exception as e:
            logging.critical(f"There was an error adding new record to {Model.__tablename__} table. Error: {str(e)}")



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
