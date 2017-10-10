from threading import Thread
from datetime import datetime
import os
import time
import sys

from Keysight_34980A.Kesight_34980A_TC_Scan import Keysight34980A_TC
from Collections.HardwareStatusInstance import HardwareStatusInstance
from Collections.ProfileInstance import ProfileInstance


from Logging.Logging import Logging


class ThermoCoupleUpdater(Thread):
    """
    This is a simply thread class that connects the hardware (Keysight34980A_TC)
    With our software interface (hwStatus.Thermocouples).

    This is one way communication, it doesn't write anything to the Keysight34980A_TC, only reads.

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
                Logging.logEvent("Event","Thread Start",
                        {"thread": "ThermoCoupleUpdater",
                         "ProfileInstance": ProfileInstance.getInstance()})
                Logging.logEvent("Debug","Status Update",
                {"message": "Starting ThermoCoupleUpdater",
                 "level":2})

                ipAddr_34980A = '192.168.99.3'
                Channel_List = "(@1001:1020,2036:2040,3001:3040)"
                hwStatus = self.hardwareStatusInstance.getInstance()

                userName = os.getlogin()

                if "root" in userName:
                    # Hasn't been tested yet
                    Tharsis = Keysight34980A_TC(ipAddr_34980A, ChannelList = Channel_List)
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

                            currentTestTemp = self.parent.zoneThreadDict["zone1"].tempGoalTemperature
                            currentPID = self.parent.zoneThreadDict["zone1"].pid.error_value
                            # if currentTestTemp < 5:
                            TCs = {
                                'time': datetime.now(),
                                'tcList': [
                                # (random.uniform(0,10)-5)
                                    {'Thermocouple': 11,'working':True, 'temp':hwStatus.Thermocouples.getTC(11).getTemp() + currentPID + 0}
                                    # {'Thermocouple': 5, 'temp': hwStatus.Thermocouples.getTC(5).getTemp() + 50},
                                    # {'Thermocouple': 2, 'temp': hwStatus.Thermocouples.getTC(2).getTemp() + 50},
                                    # {'Thermocouple': 3, 'temp': hwStatus.Thermocouples.getTC(3).getTemp() - 50,
                                    # 'userDefined':True},
                                    # {'Thermocouple': 4, 'temp': hwStatus.Thermocouples.getTC(4).getTemp() + 50,
                                    # 'userDefined':True},
                                ]
                                }
                            # elif currentTestTemp < 10:
                            # 	TCs = {
                            # 		'time': datetime.now(),
                            # 		'tcList': [
                            # 			{'Thermocouple': 1,'working':True, 'temp': currentTestTemp + 2},
                            # 		]
                            # 	}
                            # else:
                            # 	TCs = {
                            # 		'time': datetime.now(),
                            # 		'tcList': [
                            # 			{'Thermocouple': 1,'working':True, 'temp': currentTestTemp},
                            # 		]
                            # 	}

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
                        if ProfileInstance.getInstance().activeProfile:
                            Logging.logEvent("Event","ThermoCouple Reading",
                                {"message": "Current TC reading",
                                 "time":	TCs['time'],
                                 "tcList":	TCs['tcList'],
                                 "profileUUID": ProfileInstance.getInstance().zoneProfiles.profileUUID,
                                 "ProfileInstance": ProfileInstance.getInstance()}
                            )
                        else:
                            Logging.logEvent("Event","ThermoCouple Reading",
                                {"message": "Current TC reading",
                                 "time":    TCs['time'],
                                 "tcList":  TCs['tcList'],
                                 "profileUUID": "NULL",
                                 "ProfileInstance": ProfileInstance.getInstance()}
                            )

                        Logging.logEvent("Debug","Data Dump",
                            {"message": "Current TC reading",
                             "level":4,
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
                         "level":2})
                raise e
                # If you want to cleanly close things, do it here
                time.sleep(self.SLEEP_TIME)
                    # raise e
                # end of try/except
            # end of running check
        # end of while True
    # end of run()
