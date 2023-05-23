
file_path = "/etc/rc.local"
command = "su pi -c '/usr/bin/python /home/pi/fiskefelle/main.py /home/pi/fiskefelle/logs/main.log 2>&1 &'"
defaultLine = ["#!/bin/sh -e", "#", "# rc.local", "#", "# This script is executed at the end of each multiuser runlevel.", "# Make sure that the script will 'exit 0' on success or any other", "# value on error.", "#", "# In order to enable or disable this script just change the execution", "# bits", "#", "# By default this script does nothing.", "", "# Add your custom startup commands below this line"]
    
"""
_______________________ writeFile _______________________
This file a the command in the /etc/rc.local file. This command is if the python script shuld start on startup
If you want the website to not start on boot then just call writeFile()
If you want the wwbsite to start on boot then call writeFile(command)

NOTE has to be run as root

"""
def writeFile(command=None):
    with open(file_path, 'w') as f: # OPENS THE PYTHON FILE
        for line in defaultLine: # LOOPS OVER ALL OF THE DEFAULT LINES (to keep the script lokking good)
            f.writelines(line + '\n') # WRITES THE LINES

        if command != None: # IF THE COMMAND IS NOT NONE
            f.writelines(command + "\n") # WRITES THE COMMAND
        f.writelines("exit 0") # EXITS THE SCRIPT

writeFile(command)