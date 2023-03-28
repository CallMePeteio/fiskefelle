








import smbus 
import time 







class Relay(): 
    def __init__(self):


        self.bus = smbus.SMBus(1) 

        self.i2cAdress = 0x20 # SETS THE ADRESS OF THE RELAY BOARD
        self.relayDict = {"relay1": 0xFE, "relay2": 0xFD, "relay3": 0xFB, "relay4": 0xF7, "relay5": 0xEF, "relay6": 0xDF, "offAll": 0xFF, "onAll": 0x00} # MAKES A DICTIONARY, FOR TURNING ON AND OFF THE RELAY

    def switchRelay(self, command): 
        self.bus.write_byte(self.i2cAdress, self.relayDict[command])





"""
relay = Relay()
while True:
      
    relay.switchRelay("relay1")
    time.sleep(0.5)
    relay.switchRelay("offAll")
    time.sleep(0.5)
"""
