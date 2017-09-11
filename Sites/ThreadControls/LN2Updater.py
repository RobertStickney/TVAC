from threading import Thread
import os
import time
from datetime import datetime

from HouseKeeping.globalVars import debugPrint
from ThreadControls.ThreadCollection import ThreadCollection
from DataContracts.AnalogOutContract import AnalogOutContract
from DataContracts.AnalogInContract import AnalogInContract
from Collections.HardwareStatusInstance import HardwareStatusInstance

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
            debugPrint(2, "Creating ThermoCoupleUpdater")
            LN2Updater.__instance = self
            self.ThreadCollection = ThreadCollection
            self.hardwareStatusInstance = HardwareStatusInstance
            super(LN2Updater, self).__init__()

    def run(self):
        # some start up stuff here
        SLEEP_TIME = 5  # will be 30 seconds
        ln2_min = 10  # to be replaced with real value
        hwStatus = self.hardwareStatusInstance.getInstance()
        userName = os.environ['LOGNAME']

        # Not sure how much of this is relevant... Especially Kesight
        if "root" in userName:
            # Hasn't been tested yet
            AnalogOut = AnalogOutContract.AnalogOutContract()  # todo: better variable name?

        # stop when the program ends
        while True:
            if "root" in userName:
                debugPrint(4, "Pulling live data for LN2") #carry over from TCUpdater - What does this do/is it needed?
                # Hasn't been tested yet
                # LN2Platen = LN2Out.getLN2platen() for now use shroud
                LN2Shroud = AnalogOut.getLN2shroud()  # is this current LN2 val needed?
            else:
                debugPrint(4, "Generating test data for TC")
                # currentTestTemp = hwStatus.Thermocouples.getTC(1).getTemp()
                dutycyclelist = [self.ThreadCollection.zoneThreadDict["zone1"].dutycycle,
                                 self.ThreadCollection.zoneThreadDict["zone2"].dutycycle,
                                 self.ThreadCollection.zoneThreadDict["zone3"].dutycycle,
                                 self.ThreadCollection.zoneThreadDict["zone4"].dutycycle,
                                 self.ThreadCollection.zoneThreadDict["zone5"].dutycycle,
                                 self.ThreadCollection.zoneThreadDict["zone6"].dutycycle,
                                 self.ThreadCollection.zoneThreadDict["zone7"].dutycycle,
                                 self.ThreadCollection.zoneThreadDict["zone8"].dutycycle,
                                 self.ThreadCollection.zoneThreadDict["zone9"].dutycycle]
                dutycyclemin = min(dutycyclelist)

                if dutycyclemin < arb_value: # todo: arb_value to be determined
                    AnalogInContract.update()
                    #how to update LN2 (assuming this is in AnalogInContract) --> What is the structure of the dictionary? d['ADC 15'] --> LN@Shroud
