import os
import sys
import time
from datetime import datetime
from threading import Thread

from Collections.HardwareStatusInstance import HardwareStatusInstance
from Collections.ProfileInstance import ProfileInstance
from Hardware_Drivers.Keysight_34980A_TCs import Keysight_34980A_TCs
from Logging.Logging import Logging


class ThermoCoupleUpdater(Thread):
    """
    This is a simply thread class that connects the hardware (Keysight_34980A_TCs)
    With our software interface (hwStatus.Thermocouples).

    This is one way communication, it doesn't write anything to the Keysight_34980A_TCs, only reads.

    If there are errors in the thread, they will be caught, processed, and the thread restarted
    """
    __instance = None

    def __init__(self, parent):
        if ThermoCoupleUpdater.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Logging.logEvent("Debug","Status Update",
            {"message": "Creating ThermoCoupleUpdater",
             "level":2})
            ThermoCoupleUpdater.__instance = self
            self.parent = parent
            self.hardwareStatusInstance = HardwareStatusInstance
            self.SLEEP_TIME = 5 # will be 30 seconds
            super(ThermoCoupleUpdater, self).__init__()

    def run(self):
        # This makes the loop constant, even after failing, it will just restart the thread info
        while True:
            # This try is there to catch any errors that might show up
            try:
                # Thread "Start up" stuff goes here
                Logging.logEvent("Debug","Status Update",
                {"message": "Starting ThermoCoupleUpdater",
                 "level":2})

                ipAddr_34980A = '192.168.99.3'
                Channel_List = "(@1001:1020,2036:2040,3001:3040)"
                hwStatus = self.hardwareStatusInstance.getInstance()

                if os.name == "posix":
                    userName = os.environ['LOGNAME']
                else:
                    userName = "user" 

                if "root" in userName:
                    # Hasn't been tested yet
                    Tharsis = Keysight_34980A_TCs(ipAddr_34980A, ChannelList = Channel_List)
                    Tharsis.init_sys()

                while True:
                    # Setting True while testing
                    if True or ProfileInstance.getInstance().activeProfile:
                        if "root" in userName:
                            Logging.logEvent("Debug","Status Update",
                            {"message": "Pulling live data for TC",
                             "level":4})
                            # Hasn't been tested yet
                            TCs = Tharsis.getTC_Values()
                        else:
                            # We are in a test enviorment, so give it fake data

                            Logging.logEvent("Debug","Status Update",
                            {"message": "Generating test data for TC",
                             "level":4})


                            currentPID = self.parent.dutyCycleThread.zones["zone1"].pid.error_value
                            TCs = {
                                'time': datetime.now(),
                                'tcList': [
                                    {'Thermocouple': 11,'working':True, 'temp':hwStatus.Thermocouples.getTC(11).getTemp() + currentPID + 50},
                                    # {'Thermocouple': 90,'working':True, 'temp':hwStatus.Thermocouples.getTC(90).getTemp() + currentPID + 2},
                                    # {'Thermocouple': 15,'working':True, 'temp':hwStatus.Thermocouples.getTC(15).getTemp() + currentPID + 3},
                                    # {'Thermocouple': 16,'working':True, 'temp':hwStatus.Thermocouples.getTC(16).getTemp() + currentPID + 4},
                                    # {'Thermocouple': 17,'working':True, 'temp':hwStatus.Thermocouples.getTC(17).getTemp() + currentPID + 5},
                                    # {'Thermocouple': 18,'working':True, 'temp':hwStatus.Thermocouples.getTC(18).getTemp() + currentPID + 0},
                                    # {'Thermocouple': 19,'working':True, 'temp':hwStatus.Thermocouples.getTC(19).getTemp() + currentPID + 0},
                                    # {'Thermocouple': 20,'working':True, 'temp':hwStatus.Thermocouples.getTC(20).getTemp() + currentPID + 0},

                                ]
                            }

                        '''
                        TCs is a list of dicitations ordered like this....
                        {
                        'Thermocouple': tc_num,
                        'time': tc_time_offset,
                        'temp': tc_tempK,
                        'working': tc_working,
                        'alarm': tc_alarm
                        }
                        '''
                        if ProfileInstance.getInstance().recordData:
                            # Logging.logEvent("Event","ThermoCouple Reading",
                                
                            # )
                            Logging.logLiveTemperatureData({"message": "Current TC reading",
                                 "time":    TCs['time'],
                                 "tcList":  TCs['tcList'],
                                 "profileUUID": ProfileInstance.getInstance().zoneProfiles.profileUUID,
                                 "ProfileInstance": ProfileInstance.getInstance()})

                        Logging.logEvent("Debug","Data Dump",
                            {"message": "Current TC reading",
                             "level":3,
                             "dict":TCs['tcList']})

                        hwStatus.Thermocouples.update(TCs)

                        time.sleep(self.SLEEP_TIME)

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                Logging.logEvent("Error","Hardware Interface Thread",
                        {"type": exc_type,
                         "filename": fname,
                         "line": exc_tb.tb_lineno,
                         "thread": "ThermoCoupleUpdater",
                         "ProfileInstance": ProfileInstance.getInstance()
                        })
                Logging.logEvent("Debug","Status Update",
                        {"message": "There was a {} error in ThermoCoupleUpdater. File: {}:{}".format(exc_type,fname,exc_tb.tb_lineno),
                         "level":1})
                if Logging.debug:
                    raise e
                # If you want to cleanly close things, do it here
                time.sleep(self.SLEEP_TIME)
                # end of try/except
            # end of running check
        # end of while True
    # end of run()
