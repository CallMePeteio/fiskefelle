








import smbus 


class Relay(): 
    def __init__(self, i2cAdress, initialState): 
        
        if len(initialState) > 6: 
            print("WARNING: INPUTTED INITIAL STATE LIST IS LONGER THAN 6 CHANNELS")

        self.bus = smbus.SMBus(1) 
        self.i2cAdress = i2cAdress 
        self.relayState = initialState
        self.switchRelay()
        


#_______________________________ switchRelay _______________________________
# This function switches the relay board that is on the raspberry pi. The libary makers of this libary didnt do the dirty work with a libary so it is done here.
# When you write bytes to the relay board it takes in an integer value for what relays to switch, there is 64 diffrent combintations (remember all of, whitch is not done by the function)
#
# relayStateList = This is the requested relay position in a list. for example: [0,0,0,0,0,1] This will only turn on the first relay. (relaynr 1)
#
# returns None
    def switchRelay(self, relayState=None):

        if relayState != None:
            self.relayState = relayState

        relayOffset = [32,16,8,4,2,1] # THIS IS THE STATE OF THE RELAY OFFSETS, FOR CALCULATING THE REQUIRED NUMBER
        sum = 0 # THIS STORES THE FINAL SUM

        for i, num in enumerate(self.relayState): # LOOPS OVER ALL OF THE DIFFRENT VALUES
            if num == 0:
                sum += relayOffset[i] # ADDS THE NUMBER TO THE FINAL SUM
        self.bus.write_byte(self.i2cAdress, sum) # TURNS ON THE RELAYS

    def updateRelayState(self, value, index):
        self.relayState[index] = value
        self.switchRelay()






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

