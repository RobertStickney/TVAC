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
from Shi_Cryo_Pump.Shi_Mcc import Shi_Mcc

from Logging.MySql import MySQlConnect
from Logging.Logging import Logging


class VacuumControlStub(Thread):
    '''
    This class contains the main inteligences for getting and keeping the test chaber under vacuum,
    '''

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):

        Logging.logEvent("Debug","Status Update", 
        {"message": "Creating VacuumControlStub: {}",
         "level":3})

        Thread.__init__(self, group=group, target=target, name=name)
        self.args = args
        self.kwargs = kwargs

        self.zoneProfiles = ProfileInstance.getInstance().zoneProfiles
        self.gauges = PfeifferGaugeInstance.getInstance().gauges
        self.hwStatus = HardwareStatusInstance.getInstance()
        self.state = None
        self.oldState = True

        self.ShiMcc = Shi_Mcc()

        self.updatePeriod = 2




    def run(self):
        # Always run this thread
        while True:
            if self.hwStatus.vacuum:
                # With an active profile, we start putting the system under pressure
                try:
                    Logging.logEvent("Debug","Status Update", 
                    {"message": "{}: Running Vacuum Control Stub",
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
                    
                    Logging.logEvent("Debug","Status Update", 
                    {"message": "Current chamber pressure: {}".format(self.chamberPressure),
                     "level":2})

                    # calculations to get from here to there
                    if self.chamberPressure > 300: #torr?
                        # use the roughing pump to achive Rough vacuum
                        # Wait until 0.0.041 tor
                        self.state = "Atmosphere"
                    if self.chamberPressure < 300 and self.roughPumpPressure < self.cryoPumpPressure:
                        # open Cryopump-Roughing gate valve
                        # Wait until 0.041 tor
                        self.state = "Rough Vacuum"
                    if self.chamberPressure < 0.041:
                        # Alert the user they should close o-ring seal 
                        # Start the cryopump
                        self.state = "Cryo Vacuum"
                    if self.chamberPressure < 0.005 and self.ShiMcc.Get_SecondStageTemp()['data'] < 15: #torr?
                        # Close the rough gate valve
                        # Open the cryopump gate valve
                        # Wait until 10e-6 tor
                        self.state = "Strong Cryo Vacuum"
                    if self.chamberPressure < 0.00001: #torr?
                        # Wait for nothing, either the program will end, or be stopped by the safety checker
                        self.state = "Operational Vacuum"

                    Logging.logEvent("Debug","Status Update", 
                    {"message": "Current chamber state: {}".format(self.state),
                     "level":2})

                    result = {
                        'Atmosphere': self.atmosphere,
                        'Rough Vacuum': self.roughVacuum,
                        'Cryo Vacuum': self.cryoVacuum,
                        'Strong Cryo Vacuum': self.strongCryoVacuum,
                        'Operational Vacuum': self.operationalVacuum,
                    }[self.state]()


                    # switch case (ish thing) saying what you need to do to get to the point you need to be at
                    # Makin sure this still needs to be running (is there an active profile)

                    # sleep until the next time around
                    time.sleep(self.updatePeriod)


                    # TODO: Is there some safe way of taking the chamber out of vacuum?
                except Exception as e:

                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print("Error: {} in file {}:{}".format(exc_type, fname, exc_tb.tb_lineno))

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
        if self.oldState != self.state:
            # The system has just crossed over to a new point
            userName = os.environ['LOGNAME']
            if "root" in userName:
                # TODO: Read coldwater value from Compressor
        
                # Close Cryopump gate Valve 
                # I can't find cryopump, but I found this?
                self.ShiMcc.Close_PurgeValve() #line 237 Shi_MCC.py

                # Turn on Roughing Pump
                # TODO: Can you turn the roughing pump on via Shi_mcc.py? of Software??
                # Do we send an alart to the user, if they need to do this phycisally?

                # Open roughing pump valve
                self.ShiMcc.Open_RoughingValve() #line 407 Shi_MCC.py
            else:
                print("in Atomo")


    def roughVacuum(self):
        '''
        It enters this state everytime you are between 0.041 torr and 0.005 torr
        '''
        if self.oldState != self.state:
            # The system has just crossed over to a new point
            userName = os.environ['LOGNAME']
            if "root" in userName:
                # open Cryopump-Roughing gate valve
                # TODO: What command is this in Shi_Mcc.py
                pass
            else:
                print("in rough vacuum")


    def cryoVacuum(self):
        '''
        It enters this state everytime you are between 0.041 torr and 0.005
        '''
        if self.oldState != self.state:
            # The system has just crossed over to a new point
            userName = os.environ['LOGNAME']
            if "root" in userName:
                #TODO: Alert the user they should close o-ring seal 

                #TODO: starts the cryopump
                self.ShiMcc.Turn_CryoPumpOn() #line 220 ShiMcc.py
            else:
                print("In Cryo Vacuum")

    def strongCryoVacuum(self):
        '''
        It enters this state everytime you are between 0.005 torr and 0.00001
        '''
        if self.oldState != self.state:
            # The system has just crossed over to a new point
            userName = os.environ['LOGNAME']
            if "root" in userName:

                # Close the rough gate valve
                self.ShiMcc.Close_RoughingValve()

                # wait here until the valve is closed
                # This assumes it gives a True and False
                while self.ShiMcc.Get_RoughingValveState():
                    pass

                # Open the cryopump gate valve
                # I can't find cryopump, but I found this?
                self.ShiMcc.Open_PurgeValve() #line 234 Shi_MCC.py
            else:
                print("In Strong Cryo Vacuum")
        
    def operationalVacuum(self):
        '''
        It enters this state everytime you are lower than 0.00001 torr
        '''
        if self.oldState != self.state:
            # The system has just crossed over to a new point
            
            pass
            # Bakes ban happen here.
            # Thermal Profiles can start here



    # TODO: Write a wrapper around opening valves to make one final check of the pressures before we open them
