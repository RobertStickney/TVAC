from threading import Thread
import os
import time
from datetime import datetime


from Collections.HardwareStatusInstance import HardwareStatusInstance
from Collections.ProfileInstance import ProfileInstance

from Logging.Logging import Logging
# used for testing
import random

class LN2ControlStub(Thread):
    """
    docstring for LN2ControlStub
    """
    __instance = None

    def __init__(self, ThreadCollection):
        if LN2ControlStub.__instance != None: # correct to carry over from TCU.py?
            raise Exception("This class is a singleton!")
        else:
            Logging.logEvent("Debug","Status Update", 
            {"message": "LN2: Creating LN2ControlStub",
             "level":2})
            LN2ControlStub.__instance = self
            self.ThreadCollection = ThreadCollection
            self.hardwareStatus = HardwareStatusInstance
            self.SLEEP_TIME = 5  # will be 30 seconds
            super(LN2ControlStub, self).__init__()

    def run(self):
        # While true to restart the thread if it errors out
        while True:
            # Check to make sure there is an active profile
            # and that we are sitting in an operational vacuum
            # and that all drivers and updaters are running
            a_out = self.hardwareStatus.getInstance().PC_104.analog_out  # todo: better variable name?
            d_out = self.hardwareStatus.getInstance().PC_104.digital_out
            a_out.update({'LN2 Shroud': 0,'LN2 Platen': 0})
            d_out.update({'LN2-S Sol': False, 'LN2-P Sol': False, })
            if ProfileInstance.getInstance().activeProfile and HardwareStatusInstance.getInstance().OperationalVacuum:
                # try and catch anything that might go wrong
                try:
                    # some start up stuff here
                    ln2_max = 0.1
                    ln2_min = -0.2 
                    time.sleep(self.SLEEP_TIME)
                    # hwStatus = self.hardwareStatus.getInstance()
                    if os.name == "posix":
                        userName = os.environ['LOGNAME']
                    else:
                        userName = "user" 

                    # Normal program loop
                    while ProfileInstance.getInstance().activeProfile and HardwareStatusInstance.getInstance().OperationalVacuum:
                        # TODO: make sure this commented section can be deleted
                        # if "root" in userName:
                        #     Logging.debugPrint(3, "LN2: Pulling live data") #carry over from TCUpdater - What does this do/is it needed?
                        #     # Hasn't been tested yet
                        #     # LN2Platen = LN2Out.getLN2platen() for now use shroud
                        #     LN2Shroud = a_out.getLN2shroud()  # is this current LN2 val needed?
                        # else:
                        #     Logging.debugPrint(3, "LN2: Generating test data for TC")

                        dutycyclelist = []
                        platenDuty = None
                        for zoneStr in self.ThreadCollection.dutyCycleThread.zones:
                            
                            zone = self.ThreadCollection.dutyCycleThread.zones[zoneStr]
                            # If a zone doesn't have a dutyCycle, they aren't running, so we can safely ignore them
                            try:
                                if zoneStr != "zone9":
                                    dutycyclelist.append(zone.dutyCycle)
                                else:
                                    platenDuty = zone.dutyCycle
                            except Exception as e:
                                pass
                        if dutycyclelist:
                            dutycyclemin = min(dutycyclelist)
                            Logging.debugPrint(3,"Min Duty Cycle: {}".format(dutycyclemin))

                            if dutycyclemin < ln2_max: # todo: arb_value to be determined
                                # throw safety up
                                d_out.update({'LN2-S Sol': True})
                                # 2500 is the point the valve should be opened too
                                #a_out.update({'LN2 Shroud': 4095, 'LN2 Platen': 4095})
                                PercentVavleopen = 4095*(dutycyclemin-ln2_max)/(ln2_min-ln2_max)
                                if dutycyclemin < ln2_min:
                                    PercentVavleopen = 4095
                                a_out.update({'LN2 Shroud': PercentVavleopen})
                                Logging.debugPrint(3,"The Shroud LN2 should be on {}".format(PercentVavleopen))
                            else:
                                Logging.debugPrint(3,"The Shroud LN2 should be off")
                                # What's the difference between this and...
                                d_out.update({'LN2-S Sol': False})
                                a_out.update({'LN2 Shroud': 0})
                            # end of if/else
                        # end of if DutycycleList
                        if platenDuty:
                            if platenDuty < ln2_max: # todo: arb_value to be determined
                                # throw safety up
                                d_out.update({'LN2-P Sol': True})
                                # 2500 is the point the valve should be opened too
                                #a_out.update({'LN2 Shroud': 4095, 'LN2 Platen': 4095})
                                PercentVavleopen = 4095*(platenDuty-ln2_max)/(ln2_min-ln2_max)
                                if platenDuty < ln2_min:
                                    PercentVavleopen = 4095
                                a_out.update({'LN2 Platen': PercentVavleopen})
                                Logging.debugPrint(3,"The Platen LN2 should be on {}".format(PercentVavleopen))
                            else:
                                Logging.debugPrint(3,"The Platen LN2 should be off")
                                # What's the difference between this and...
                                d_out.update({'LN2-P Sol': False, })
                                a_out.update({'LN2 Platen': 0})
                        time.sleep(self.SLEEP_TIME)
                    # end of Inner While True
                except Exception as e:
                    Logging.debugPrint(1, "Error in run, LN2 Control Stub: {}".format(str(e)))
                    if Logging.debug:
                        raise e
                # end of try catch
            else:
                Logging.debugPrint(3,"LN2: AP: {}, Vacuum: {}".format(ProfileInstance.getInstance().activeProfile,HardwareStatusInstance.getInstance().OperationalVacuum))
            # end of If should be running
            time.sleep(self.SLEEP_TIME)

        # end of outter while true
    # end of run()
# end of class
