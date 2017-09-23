from threading import Thread
import json
import uuid
import time
import datetime
import sys
import os


from Collections.ProfileInstance import ProfileInstance
from Collections.PfeifferGaugeInstance import PfeifferGaugeInstance
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
        self.gauges = PfeifferGaugeInstance.getInstance().gauges
        self.state = None




    def run(self):
        # Always run this thread
        while True:
            if self.zoneProfiles.activeProfile:
                # With an active profile, we start putting the system under pressure
                try:
                    Logging.logEvent("Debug","Status Update", 
                    {"message": "{}: Running HW control Thread".format(self.args[0]),
                     "level":2})
         
                    # Setup code is here
                    if self.state:
                        self.oldState = self.state

                    # connection to the MCC
                    # JK, it's already done in the MCC control stub

                    # Reading of pressure gauges, to figure out where the system is

                    # When you know what the pressure is, you know what to do go get into pressure
                    self.cryoPumpPressure = self.gauges.get_pressure_cryopump()
                    self.chamberPressure = self.gauges.get_pressure_chamber()
                    self.roughPumpPressure = self.gauges.get_pressure_roughpump()
                    # TODO: Is this pressure result in torr?

                    # learning from Zoneprofiles what vacuum state the system needs to be in
                    # If it's here, you want the vacuum to be on
                    
                    # calculations to get from here to there
                    if self.chamberPressure > 300: #torr?
                        # use the roughing pump to achive Rough vacuum
                        # Wait until 0.0.041 tor
                        self.state = "Atmosphere"
                    if self.chamberPressure < 0.041 and self.roughPumpPressure < self.cryoPumpPressure:
                        # open Cryopump-Roughing gate valve
                        # Alert the user they should close o-ring seal 
                        # Wait until 0.005 tor
                        self.state = "Rough Cacuum"
                    if self.chamberPressure < 0.005: #torr?
                        # Use CryoPump to achive Cryo Vacuum
                        # Start the cryopump
                        # Close the rough gate valve
                        # Open the cryopump gate valve
                        # Wait until 10e-6 tor
                        self.state = "Cryo Vacuum"
                    if self.chamberPressure < 0.00001: #torr?
                        # Wait for nothing, either the program will end, or be stopped by the safety checker
                        self.state = "Operational Vacuum"

                        

                    result = {
                        'Atmosphere': self.atmosphere,
                        'Rough Vacuum': self.roughVacuum,
                        'Cryo Vacuum': self.cryoVacuum,
                        'Operational Vacuum': self.operationalVacuum,
                    }[self.state]()


                    # switch case (ish thing) saying what you need to do to get to the point you need to be at
                    # Makin sure this still needs to be running (is there an active profile)

                    # sleep until the next time around
                    time.sleep(self.updatePeriod)


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

    def atmosphere(self):
        '''
        It enters this state everytime you are at atmosphere pressure
        '''
        # TODO: Read coldwater value from Compressor
        if self.oldState != self.state:
            # The system has just crossed over to a new point

            # Close Cryopump gate Valve 
            # Turn on Roughing Pump
            # Open roughing pump valve

    def roughVacuum(self):
        if self.oldState != self.state:
            # The system has just crossed over to a new point
            pass
        pass
    def cryoVacuum(self):
        if self.oldState != self.state:
            # The system has just crossed over to a new point
            pass
        pass
    def operationalVacuum(self):
        if self.oldState != self.state:
            # The system has just crossed over to a new point
            pass
        pass

