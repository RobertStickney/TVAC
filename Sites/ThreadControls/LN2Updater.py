from threading import Thread
import os
import time
from datetime import datetime


from Collections.HardwareStatusInstance import HardwareStatusInstance

from Logging.Logging import Logging
# used for testing
import random

class LN2Updater(Thread):
    """
    docstring for LN2Updater
    """
    __instance = None

    def __init__(self, ThreadCollection):
        if LN2Updater.__instance != None: # correct to carry over from TCU.py?
            raise Exception("This class is a singleton!")
        else:
            Logging.logEvent("Debug","Status Update", 
            {"message": "Creating ThermoCoupleUpdater",
             "level":2})
            LN2Updater.__instance = self
            self.ThreadCollection = ThreadCollection
            self.hardwareStatus = HardwareStatusInstance
            self.SLEEP_TIME = 5  # will be 30 seconds
            super(LN2Updater, self).__init__()

    def run(self):
        # some start up stuff here
        ln2_min = .10  # to be replaced with real value
        hwStatus = self.hardwareStatus.getInstance()
        userName = os.environ['LOGNAME']
        d_out = hwStatus.PC_104.digital_out

        if "root" in userName:
            # Hasn't been tested yet
            AnalogOut = hwStatus.PC_104.analog_out  # todo: better variable name?

        # stop when the program ends
        while True:
            if "root" in userName:
                Logging.debugPrint(4, "Pulling live data for LN2") #carry over from TCUpdater - What does this do/is it needed?
                # Hasn't been tested yet
                # LN2Platen = LN2Out.getLN2platen() for now use shroud
                LN2Shroud = AnalogOut.getLN2shroud()  # is this current LN2 val needed?
            else:
                Logging.debugPrint(4, "Generating test data for TC")

            dutycyclemin =  1
            dutycyclelist = []
            for zoneStr in self.ThreadCollection.zoneThreadDict:
                zone = self.ThreadCollection.zoneThreadDict[zoneStr]
                if zone.running:
                    print("Zone {} is {} running".format(zoneStr, "" if zone.running else "not"))
                    dutycyclelist.append(zone.dutyCycle)

            if dutycyclelist:
                dutycyclemin = min(dutycyclelist)
                # print("Min Duty Cycle: {}".format(dutycyclemin))

                if dutycyclemin < ln2_min: # todo: arb_value to be determined
                    # 2500 is the point the valve should be opened too
                    print("The LN2 should be on")
                    d_out.update({"LN2-S EN":True})
                    d_out.update({"LN2-Sol EN":True})
                    
                    AnalogOut.update({"LN2 Platen":2500})
                    # throw safety up
                else:
                    print("The LN2 should be off")
                    d_out.update({"LN2-S EN":False})
                    d_out.update({"LN2-Sol EN":False})
                    AnalogOut.update({"LN2 Platen":0})
                    #how to update LN2 (assuming this is in AnalogInContract) --> What is the structure of the dictionary? d['ADC 15'] --> LN@Shroud
            time.sleep(self.SLEEP_TIME)