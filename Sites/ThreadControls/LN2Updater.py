from threading import Thread
import os
import time
from datetime import datetime


from Collections.HardwareStatusInstance import HardwareStatusInstance
from Collections.ProfileInstance import ProfileInstance

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
        # Always run this thread
        while True:
            # Check to make sure there is an active profile
            # and that we are sitting in an operational vacuum
            if ProfileInstance.getInstance().activeProfile and HardwareStatusInstance.getInstance().OperationalVacuum:
                # some start up stuff here
                ln2_min = 0  
                time.sleep(5)
                # hwStatus = self.hardwareStatus.getInstance()
                userName = os.environ['LOGNAME']

                a_out = self.hardwareStatus.getInstance().PC_104.analog_out  # todo: better variable name?
                d_out = self.hardwareStatus.getInstance().PC_104.digital_out

                # if "root" in userName:
                #     # Hasn't been tested yet

                # stop when the program ends
                while True:
                    if "root" in userName:
                        Logging.debugPrint(4, "Pulling live data for LN2") #carry over from TCUpdater - What does this do/is it needed?
                        # Hasn't been tested yet
                        # LN2Platen = LN2Out.getLN2platen() for now use shroud
                        LN2Shroud = a_out.getLN2shroud()  # is this current LN2 val needed?
                    else:
                        Logging.debugPrint(4, "Generating test data for TC")

                    dutycyclelist = []
                    for zoneStr in self.ThreadCollection.zoneThreadDict:
                        zone = self.ThreadCollection.zoneThreadDict[zoneStr]
                        if zone.running:
                            # print("Zone {} is {} running".format(zoneStr, "" if zone.running else "not"))
                            dutycyclelist.append(zone.dutyCycle)

                    if dutycyclelist:
                        dutycyclemin = min(dutycyclelist)
                        Logging.debugPrint(4,"Min Duty Cycle: {}".format(dutycyclemin))

                        if dutycyclemin < ln2_min: # todo: arb_value to be determined
                            # throw safety up
                            Logging.debugPrint(4,"The LN2 should be on")
                            # What's the difference between this and...
                            d_out.update({'LN2-S Sol': True, 'LN2-P Sol': True, })
                            # this
                            # d_out.update({"LN2-S EN":True})
                            # d_out.update({"LN2-Sol EN":True})


                            # 2500 is the point the valve should be opened too
                            a_out.update({'LN2 Shroud': 4095, 'LN2 Platen': 4095}) 
                           
                        else:
                            Logging.debugPrint(4,"The LN2 should be off")
                            # What's the difference between this and...
                            d_out.update({'LN2-S Sol': False, 'LN2-P Sol': False, })
                            # this
                            # d_out.update({"LN2-S EN":False})
                            # d_out.update({"LN2-Sol EN":False})


                            # 2500 is the point the valve should be opened too
                            a_out.update({'LN2 Shroud': 0, 'LN2 Platen': 0})
                            #how to update LN2 (assuming this is in AnalogInContract) --> What is the structure of the dictionary? d['ADC 15'] --> LN@Shroud
                    time.sleep(self.SLEEP_TIME)