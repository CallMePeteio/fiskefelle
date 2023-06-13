



import smbus 



"""
_________________________ Relay _________________________
This class is for controling the 6ch relay board hat that is on the raspberry pi
link to board documentation: https://www.osaelectronics.com/learn/tutorials/6-channel-relay-board-quick-start-guide/

i2cAdress: This is the i2c adress of the board (stock 0x20) (hex)
initialState: This is the state of the relays that is going to be selected when the class is created. for example if you want the first relay to be on then input: [1,0,0,0,0,0] (list)

"""


class Relay(): 
    def __init__(self, i2cAdress, initialState): 
        self.bus = smbus.SMBus(1) # MAKES THE BUS OBJECT
        self.i2cAdress = i2cAdress # SETS THE I2C ADRESS OF THE HAT
        self.relayState = initialState # SETS THE INITIAL STATE OF THE RELAY HAT
        self.switchRelay() # SWITCHES THE RLEAY TO THE RELAY INITIAL STATE
        


#_______________________________ switchRelay _______________________________

# This function switches the relay board that is on the raspberry pi. The libary makers of this libary didnt do the dirty work with a libary so it is done here.
# When you write bytes to the relay board it takes in an integer value for what relays to switch, there is 64 diffrent combintations (remember all of, whitch is not done by the function)
#
# relayStateList = This is the requested relay position in a list. for example: [0,0,0,0,0,1] This will only turn on the first relay. (relaynr 1)
#
# returns None
    def switchRelay(self, relayState=None):

        if relayState != None: # IF THE USER WANTS TO UPDATE THE RELAY POSITION
            self.relayState = relayState # SETS THE INPUT RELAY STATE, TO THE CURRENT FOR UPDATING

        relayOffset = [32,16,8,4,2,1] # THIS IS THE STATE OF THE RELAY OFFSETS, FOR CALCULATING THE REQUIRED NUMBER
        sum = 0 # THIS STORES THE FINAL SUM

        for i, num in enumerate(self.relayState): # LOOPS OVER ALL OF THE DIFFRENT VALUES
            if num == 0:
                sum += relayOffset[i] # ADDS THE NUMBER TO THE FINAL SUM
        self.bus.write_byte(self.i2cAdress, sum) # TURNS ON THE RELAYS


#____________________________ updateRelayState _____________________________
# This functoin is usually used to update only one of the relay channels. 
# It a value in the "self.relayState", indexed by the input in the function
#
# Value: This is the value you want to change to, usually 0 and 1 (int)
# index: This is the index you want the value to be changed in usually between 0-5 (int)
#
# returns None
    def updateRelayState(self, value, index):
        self.relayState[index] = value # CHANGES THE REQUESTED INDEX TO THE REQUESTED VALUE
        self.switchRelay() # SWITCHES THE RELAYS TO THE REQUESTED POSITION






"""


EXAMPLE CODE: 

import time 
relay = Relay(0x20, [0,0,0,0,0,0])
while True:
    relay.switchRelay([1,0,0,0,0,0])
    time.sleep(0.5)
    relay.updateRelayState(1, 5)
    time.sleep(0.5)
    relay.switchRelay([0,0,0,0,0,0])
    time.sleep(0.5)

    




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

