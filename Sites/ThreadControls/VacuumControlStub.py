from threading import Thread
import json
import uuid
import time
import datetime
import sys
import os


from Collections.ProfileInstance import ProfileInstance
from Collections.HardwareStatusInstance import HardwareStatusInstance
from PID.PID import PID

from Logging.MySql import MySQlConnect
from Logging.Logging import Logging


class HardWareControlStub(Thread):
    '''
    This class contains the main inteligences for getting and keeping the test chaber under vacuum,

    '''

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):

        Logging.logEvent("Debug","Status Update", 
        {"message": "Creating HardWareControlStub: {}".format(args[0]),
         "level":3})

        Thread.__init__(self, group=group, target=target, name=name)
        self.args = args
        self.kwargs = kwargs

        self.zoneProfiles = ProfileInstance.getInstance().zoneProfiles
        # self.zoneProfile = self.zoneProfiles.getZone(self.args[0])
        # self.updatePeriod = self.zoneProfiles.updatePeriod
        # self.d_out = HardwareStatusInstance.getInstance().PC_104.digital_out



        self.tempGoalTemperature = 0
        self.pid = PID()

        self.maxTempRisePerMin = 10
        self.maxTempRisePerUpdate = (self.maxTempRisePerMin/60)*self.updatePeriod



    def run(self):
        # TODO: You can't run more than one test, it will need to updated a bit to make that work
        # Always run this thread
        while True:
            if self.zoneProfiles.activeProfile:
                try:
                    Logging.logEvent("Debug","Status Update", 
                    {"message": "{}: Running HW control Thread".format(self.args[0]),
                     "level":2})
         
                    Logging.logEvent("Event","Start Profile", 
                        {'time': datetime.time()})

                    # Setup code is here
                    # connection to the MCC
                    # Reading of pressure gauges, to figure out where the system is
                    # learning from Zoneprofiles what vacuum state the system needs to be in
                    # calculations to get from here to there

                    # Program loop is here
                    while True:

                        # Reading of pressure gauges
                        # switch case (ish thing) saying what you need to do to get to the point you need to be at
                        # Makin sure this still needs to be running (is there an active profile)

                        # sleep until the next time around
                        time.sleep(self.updatePeriod)
                    # end of inner while True
                    # end of test

                    # TODO: Is there some safe way of taking the chamber out of vacuum?
                except Exception as e:

                    # exc_type, exc_obj, exc_tb = sys.exc_info()
                    # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    # print("Error: {} in file {}:{}".format(exc_type, fname, exc_tb.tb_lineno))

                    # FileCreation.pushFile("Error",self.zoneUUID,'{"errorMessage":"%s"}'%(e))
                    self.running = False
                    ProfileInstance.getInstance().zoneProfiles.activeProfile = False
                    raise e
                # end of try, catch
            # end of running check
        # end of outter while True
    # end of run()

