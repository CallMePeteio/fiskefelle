








import smbus 
import time 
import random







# Test program for 6 Ch Relay Board RLB0665N 

# Imports Section 
import smbus 
import time 

# Initial Setup 
RELAY1 = 0xFE 
RELAY2 = 0xFD 
RELAY3 = 0xFB 
RELAY4 = 0xF7 
RELAY5 = 0xEF 
RELAY6 = 0xDF 

bus = smbus.SMBus(1) 

# Set the I2C address 
PCF8574_addr = 0x20 

# Run the program 





"""
relaystate = inputted number

[1,1,1,1,1,0] = 1
[1,1,1,1,0,1] = 2
[1,1,1,1,0,0] = 3

[1,1,1,0,1,1] = 4
[1,1,1,0,1,0] = 5
[1,1,1,0,0,1] = 6
[1,1,1,0,0,0] = 7


[1,1,0,1,1,1] = 8
[1,1,0,1,1,0] = 9
[1,1,0,1,0,1] = 10
[1,1,0,1,0,0] = 11

[1,1,0,0,1,1] = 12
[1,1,0,0,1,0] = 13
[1,1,0,0,0,1] = 14
[1,1,0,0,0,0] = 15

"""

#_______________________________ switchRelay _______________________________
# This function switches the relay board that is on the raspberry pi. The libary makers of this libary didnt do the dirty work with a libary so it is done here.
# When you write bytes to the relay board it takes in an integer value for what relays to switch, there is 64 diffrent combintations (remember all of, whitch is not done by the function)
#
# relayStateList = This is the requested relay position in a list. for example: [0,0,0,0,0,1] This will only turn on the first relay. (relaynr 1)
#
# returns None

def switchRelay(relayStateList):
    relayOffset = [32,16,8,4,2,1] # THIS IS THE STATE OF THE RELAY OFFSETS, FOR CALCULATING THE REQUIRED NUMBER
    sum = 0 # THIS STORES THE FINAL SUM

    for i, num in enumerate(relayStateList): # LOOPS OVER ALL OF THE DIFFRENT VALUES
        if num == 0:
            sum += relayOffset[i] # ADDS THE NUMBER TO THE FINAL SUM
    bus.write_byte(PCF8574_addr, sum) # TURNS ON THE RELAYS

relayState = [0,0,0,0,0,1]





while True: 
    relayState = [random.randint(0,1), random.randint(0,1), random.randint(0,1), random.randint(0,1), random.randint(0,1), random.randint(0,1)]
    switchRelay(relayState)

    time.sleep(0.2)





"""
relay = Relay()
while True:
      
    relay.switchRelay("relay1")
    time.sleep(0.5)
    relay.switchRelay("offAll")
    time.sleep(0.5)
"""
