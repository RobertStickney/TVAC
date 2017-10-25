from threading import Thread
import json
import uuid
import time
import datetime
import sys
import os


from Collections.ProfileInstance import ProfileInstance
from Collections.HardwareStatusInstance import HardwareStatusInstance

from Logging.MySql import MySQlConnect
from Logging.Logging import Logging


class VacuumControlStub(Thread):
    '''
    This class contains the main inteligences for getting and keeping the test chaber under vacuum,
    '''

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):

        Logging.logEvent("Debug","Status Update", 
        {"message": "Creating VacuumControlStub:",
         "level": 3})

        Thread.__init__(self, group=group, target=target, name=name)
        self.args = args
        self.kwargs = kwargs

        self.zoneProfiles = ProfileInstance.getInstance().zoneProfiles
        self.profile = ProfileInstance.getInstance()
        self.hw = HardwareStatusInstance.getInstance()
        self.state = None
        self.opVac = 2e-6
        self.oldState = True

        self.updatePeriod = 1


    def run(self):
        # While true to restart the thread if it errors out
        while True:
            # This has no startup, but should wait until all drivers and updaters are running
            Logging.logEvent("Debug","Status Update",
                {"message": "Starting VacuumControlStub",
                 "level":2})            
            try:
                while self.wait_for_hardware():  # Wait for hardware drivers to read sensors.
                    Logging.logEvent("Debug", "Status Update",
                                     {"message": "VacuumControlStub waiting for the hardware to be read.",
                                      "level": 5})
                    time.sleep(1)
                self.determin_current_vacuum_state()
                while True:
                    if self.profile.vacuumWanted:
                        # With an active profile, we start putting the system under pressure
             
                        Logging.logEvent("Debug","Status Update", 
                        {"message": "Running Vacuum Control Stub",
                         "level":4})
                        # Setup code is here

                        # connection to the MCC
                        # JK, it's already done in the MCC control stub

                        # Reading of pressure gauges, to figure out where the system is

                        # When you know what the pressure is, you know what to do go get into pressure
                        self.cryoPumpPressure = self.hw.PfeifferGuages.get_cryopump_pressure()
                        self.chamberPressure = self.hw.PfeifferGuages.get_chamber_pressure()
                        self.roughPumpPressure = self.hw.PfeifferGuages.get_roughpump_pressure()

                        # learning from Zoneprofiles what vacuum state the system needs to be in
                        # If it's here, you want the vacuum to be on
                        
                        Logging.logEvent("Debug","Status Update", 
                        {"message": "Current chamber pressure: {}".format(self.chamberPressure),
                         "level":4})

                        {
                            'Atm: Not Ready':                       self.state_00,
                            'Atm: Sys Ready':                       self.state_01,
                            'PullingVac: Start':                    self.state_02,
                            'PullingVac: RoughingCryoP':            self.state_03,
                            'PullingVac: CryoCool; Rough Chamber':  self.state_04,
                            'PullingVac: Cryo Pumping Chamber':     self.state_05,
                            'Operational Vacuum: Cryo Pumping':     self.state_06,
                            'Operational Vacuum':                   self.state_07,
                            'Non-Operational High Vacuum':          self.state_08,
                        }[self.state]()
                        # TODO: Add States for Is there some safe way of taking the chamber out of vacuum?

                        Logging.logEvent("Debug","Status Update", 
                        {"message": "Current chamber state: {}".format(self.state),
                         "level": 4})

                        if "Operational-Vacuum" in self.state:
                            self.hw.OperationalVacuum = True
                        else:
                            # #TODO: If you are in debugging mode, you can run as if you were in vacuum (take this out for last testing)
                            # if Logging.debug:
                            #     self.hw.OperationalVacuum = True
                            # else:
                            self.hw.OperationalVacuum = False

                        # sleep until the next time around
                        time.sleep(self.updatePeriod)

                    # End of inner if
                    else: 
                        time.sleep(1)
                # end of inner while True
            except Exception as e:

                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print("Error: {} in file {}:{}".format(exc_type, fname, exc_tb.tb_lineno))

                # FileCreation.pushFile("Error",self.zoneUUID,'{"errorMessage":"%s"}'%(e))
                ProfileInstance.getInstance().zoneProfiles.activeProfile = False
                Logging.debugPrint(1, "Error in check run, vacuum Control Stub: {}".format(str(e)))
                if Logging.debug:
                    raise e
            # end of try, catch
        # end of outer while true
    # end of run()

    def state_00(self):  # Atm: Not Ready
        if (self.hw.PC_104.digital_out.getVal('CryoP GateValve') is False) and \
                (self.hw.PC_104.digital_out.getVal('RoughP GateValve') is False) and \
                (self.hw.PC_104.digital_out.getVal('RoughP_On_Sw') == False) and \
                (self.cryoPumpPressure > 100) and \
                (self.chamberPressure > 100) and \
                (self.roughPumpPressure > 100):
            self.state = 'Atm: Sys Ready'

    def state_01(self):  # Atm: Sys Ready
        if (self.hw.PC_104.digital_out.getVal('CryoP GateValve') is True) or \
                (self.hw.PC_104.digital_out.getVal('RoughP GateValve') is True) or \
                (self.hw.PC_104.digital_out.getVal('RoughP_On_Sw') is True):
            self.state = 'Atm: Not Ready'
        if self.profile.vacuumWanted is True:
            self.state = 'PullingVac: Start'
            self.hw.PC_104.digital_out.update({'RoughP Pwr Relay': True})
            time.sleep(1)
            self.hw.PC_104.digital_out.update({'RoughP PurgeGass': True})
            time.sleep(1)  # TODO: replace sleep with Roughing pump Gate valve check and power check
            # Turn on Roughing Pump
            self.hw.PC_104.digital_out.update({'RoughP Start': True})
        # Todo: Add vacuum not wanted state move.

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
                self.hw.PC_104.digital_out.update({'CryoP GateValve': False})
                # TODO: Add check for CryoP GateValve closed state.
                # Prep the on Roughing Pump
                self.hw.PC_104.digital_out.update({'RoughP Pwr Relay': True})
                time.sleep(0.2)
                self.hw.PC_104.digital_out.update({'RoughP GateValve': True})
                time.sleep(0.2)
                self.hw.PC_104.digital_out.update({'RoughP PurgeGass': True})
                time.sleep(1)  # TODO: replace sleep with Roughing pump Gate valve check and power check
                # Turn on Roughing Pump
                self.hw.PC_104.digital_out.update({'RoughP Start': True})
                # Do we send an alart to the user, if they need to do this phycisally?

            else:
                print("in Atomo")


    def state_02(self):  # PullingVac: Start
        if (self.profile.vacuumWanted is True) and \
                (self.roughPumpPressure < 70):
            self.state = 'PullingVac: RoughingCryoP'
            self.hw.Shi_MCC_Cmds.append(['Open_RoughingValve'])
        # Todo: Add vacuum not wanted state move.

    def roughVacuum(self):
        '''
        It enters this state everytime you are between 0.040 torr and 0.005 torr
        '''
        if (self.oldState != self.state):  # and (self.oldState == "Atmosphere"):
            Logging.logEvent("Debug", "Status Update",
                             {"message": "Entering Rough vacuum. Ruffing the Cryo Pump.",
                              "level": 1})
            # The system has just crossed over to a new point
            userName = os.environ['LOGNAME']
            if "root" in userName:
                # open Cryopump-Roughing gate valve
                self.hw.Shi_MCC_Cmds.append(['Close_PurgeValve'])
                time.sleep(2)
                self.hw.Shi_MCC_Cmds.append(['Open_RoughingValve'])
                self.hw.Shi_MCC_Cmds.append(['FirstStageTempCTL', 50, 3])
                self.hw.Shi_MCC_Cmds.append(['SecondStageTempCTL', 10])
            else:
                Logging.logEvent("Debug", "Status Update",
                                 {"message": "In Rough vacuum.",
                                  "level": 4})

    def state_03(self):  # PullingVac: RoughingCryoP
        if (self.profile.vacuumWanted is True) and \
                (self.cryoPumpPressure < 45e-3):
            self.state = 'PullingVac: CryoCool; Rough Chamber'
            self.hw.Shi_MCC_Cmds.append(['Close_RoughingValve'])
            time.sleep(2)
            self.hw.Shi_Compressor_Cmds.append('on')
            self.hw.Shi_MCC_Cmds.append(['FirstStageTempCTL', 50, 3])
            self.hw.Shi_MCC_Cmds.append(['SecondStageTempCTL', 10])
            time.sleep(4)
            self.hw.Shi_MCC_Cmds.append(['Turn_CryoPumpOn'])
            time.sleep(2)
            self.hw.PC_104.digital_out.update({'RoughP GateValve': True})
        # Todo: Add vacuum not wanted state move.

    def crossoverVacuum(self):
        '''
        It enters this state everytime you are between 0.041 torr and 0.005
        '''
        if (self.oldState != self.state):
            Logging.logEvent("Debug", "Status Update",
                             {"message": "Entering Crossover Vacuum from Rough vacuum. Cryo pump On.",
                              "level": 1})
            # The system has just crossed over to a new point
            userName = os.environ['LOGNAME']
            if "root" in userName:
                #TODO: Alert the user they should close o-ring seal 
                self.hw.Shi_MCC_Cmds.append(['Close_RoughingValve'])
                time.sleep(2)
                # Starting the Cryppump:
                #TODO: starts the Compressor
                # self.hw.Shi_compressor_Cmds.append([''])
                self.hw.Shi_MCC_Cmds.append(['Turn_CryoPumpOn'])
            else:
                print("In Crossover Vacuum")

    def state_04(self):  # PullingVac: CryoCool; Rough Chamber
        if (self.profile.vacuumWanted is True) and \
                (self.hw.ShiCryopump.get_mcc_status('Stage 2 Temp') < 15) and \
                (self.chamberPressure < 45e-3):
            self.state = 'PullingVac: Cryo Pumping Chamber'
            self.hw.PC_104.digital_out.update({'RoughP GateValve': False})
            # wait here until the valve is closed
            # TODO Replace Sleep with a check of the Gate valve switches
            time.sleep(5)
            # Open the cryopump gate valve
            self.hw.PC_104.digital_out.update({'CryoP GateValve': True})
            # TODO Add a check of the Gate valve switches - Keep Sleep
            time.sleep(10)
            # Open the cryopump gate valve
            self.hw.PC_104.digital_out.update({'RoughP Pwr Relay': False})
            time.sleep(2)
            self.hw.PC_104.digital_out.update({'RoughP PurgeGass': False})
        # Todo: Add vacuum not wanted state move.

    def CryoVacuum(self):
        '''
        It enters this state everytime you are between 0.005 torr and 0.00001
        '''
        if (self.oldState != self.state):
            # The system has just crossed over to a new point
            userName = os.environ['LOGNAME']
            if "root" in userName:

                # Close the rough gate valve
                self.hw.PC_104.digital_out.update({'RoughP GateValve': False})

                # wait here until the valve is closed
                # TODO Replace Sleep with a check of the Gate valve switches
                time.sleep(4)

                # Open the cryopump gate valve
                self.hw.PC_104.digital_out.update({'CryoP GateValve': True})
                # TODO Add a check of the Gate valve switches - Keep Sleep
                time.sleep(4)

                # Open the cryopump gate valve
                self.hw.PC_104.digital_out.update({'RoughP Pwr Relay': False})
                time.sleep(2)
                self.hw.PC_104.digital_out.update({'RoughP PurgeGass': False})

            else:
                print("In Strong Cryo Vacuum")
        
    def state_05(self):  # PullingVac: Cryo Pumping Chamber
        if (self.profile.vacuumWanted is True) and \
                (self.chamberPressure < self.opVac):
            self.state = 'PullingVac: Cryo Pumping Chamber'
        # Todo: Add vacuum not wanted state move.


    def operationalVacuum(self):
        '''
        It enters this state everytime you are lower than 0.00001 torr
        '''
        if self.oldState != self.state:
            # The system has just crossed over to a new point
            print("In Operational Vacuum")
            self.zoneProfiles.updateThermalStartTime(time.time())
            # Bakes ban happen here.
            # Thermal Profiles can start here

    def state_06(self):  # Operational Vacuum: Cryo Pumping
        if (self.profile.vacuumWanted is True) and \
                (self.hw.PC_104.digital_out.getVal('CryoP GateValve') is False) and \
                (self.chamberPressure < self.opVac):
            self.state = 'Operational Vacuum'
        if self.chamberPressure > self.opVac:
            self.state = 'Non-Operational High Vacuum'

    def state_07(self):  # Operational Vacuum
        if (self.profile.vacuumWanted is True) and \
                (self.hw.PC_104.digital_out.getVal('CryoP GateValve') is True) and \
                (self.chamberPressure < self.opVac):
            self.state = 'Operational Vacuum: Cryo Pumping'
        if self.chamberPressure > self.opVac:
            self.state = 'Non-Operational High Vacuum'

    def state_08(self):  # Non-Operational High Vacuum
        pass

    def wait_for_hardware(self):
        ready = True
        ready &= self.hw.PC_104.digital_out.getVal('LN2_P_Sol_Open') is not None
        ready &= self.hw.PC_104.digital_out.getVal('LN2_P_Sol_Open_WF') is not None
        ready &= self.hw.PC_104.digital_out.getVal('LN2_P_Sol_Closed') is not None
        ready &= self.hw.PC_104.digital_out.getVal('LN2_P_Sol_Closed_WF') is not None
        ready &= self.hw.PC_104.digital_out.getVal('LN2_S_Sol_Open') is not None
        ready &= self.hw.PC_104.digital_out.getVal('LN2_S_Sol_Open_WF') is not None
        ready &= self.hw.PC_104.digital_out.getVal('LN2_S_Sol_Closed') is not None
        ready &= self.hw.PC_104.digital_out.getVal('LN2_S_Sol_Closed_WF') is not None
        ready &= self.hw.PC_104.digital_out.getVal('CryoP_GV_Open') is not None
        ready &= self.hw.PC_104.digital_out.getVal('CryoP_GV_Open_WF') is not None
        ready &= self.hw.PC_104.digital_out.getVal('CryoP_GV_Closed') is not None
        ready &= self.hw.PC_104.digital_out.getVal('CryoP_GV_Closed_WF') is not None
        ready &= self.hw.PC_104.digital_out.getVal('RoughP_Powered') is not None
        ready &= self.hw.PC_104.digital_out.getVal('RoughP_Powered_WF') is not None
        ready &= self.hw.PC_104.digital_out.getVal('RoughP_On_Sw') is not None
        ready &= self.hw.PC_104.digital_out.getVal('RoughP_On_Sw_WF') is not None
        ready &= self.hw.PfeifferGuages.get_roughpump_pressure() is not None
        ready &= self.hw.PfeifferGuages.get_chamber_pressure() is not None
        ready &= self.hw.PfeifferGuages.get_cryopump_pressure() is not None
        ready &= self.hw.ShiCryopump.get_mcc_params('Elapsed Time') is not None
        ready &= self.hw.ShiCryopump.get_mcc_params('Tc Pressure State') is not None
        ready &= self.hw.ShiCryopump.get_mcc_status('Stage 1 Temp') is not None
        ready &= self.hw.ShiCryopump.get_mcc_status('Stage 2 Temp') is not None
        ready &= self.hw.ShiCryopump.get_compressor('Helium Discharge Temperature') is not None
        ready &= self.hw.ShiCryopump.get_compressor('Water Outlet Temperature') is not None
        ready &= self.hw.ShiCryopump.get_compressor('System ON') is not None
        return ready

    def determin_current_vacuum_state(self):
        if (self.chamberPressure < self.opVac) and \
                (self.hw.ShiCryopump.get_mcc_status('Stage 2 Temp') < 20):
            if self.hw.PC_104.digital_out.getVal('CryoP GateValve'):
                return 'Operational Vacuum: Cryo Pumping'
            else:
                return 'Operational Vacuum'
        else:
            return 'Atm: Sys Ready'

    # TODO: Write a wrapper around opening valves to make one final check of the pressures before we open them
