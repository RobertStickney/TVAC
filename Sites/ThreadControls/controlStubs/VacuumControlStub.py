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
        self.state = None;
        self.pres_opVac = 9e-6
        self.pres_atm = 100
        self.pres_cryoP_Prime = 45e-6
        self.pres_chamber_crossover = 40e-6
        self.pres_chamber_ = 40e-6

        self.updatePeriod = 1

        # # FOR TESTING ################################
        # self.state = "Operational Vacuum"
        # self.hw.OperationalVacuum = True
        # # FOR TESTING ################################

        if os.name == "posix":
            userName = os.environ['LOGNAME']
        else:
            userName = "user" 
        if "root" in userName:
            pass
        else: 
            self.zoneProfiles.updateThermalStartTime(time.time())


    def run(self):
        # While true to restart the thread if it errors out
        while True:
            # This has no startup, but should wait until all drivers and updaters are running
            Logging.logEvent("Debug","Status Update",
                {"message": "Starting VacuumControlStub",
                 "level":2})            
            try:
                while not self.wait_for_hardware():  # Wait for hardware drivers to read sensors.
                    Logging.logEvent("Debug", "Status Update",
                                     {"message": "VacuumControlStub waiting for the hardware to be read.",
                                      "level": 4})
                    time.sleep(1)
                self.cryoPumpPressure = self.hw.PfeifferGuages.get_cryopump_pressure()
                self.chamberPressure = self.hw.PfeifferGuages.get_chamber_pressure()
                self.roughPumpPressure = self.hw.PfeifferGuages.get_roughpump_pressure()

                self.state = self.determin_current_vacuum_state()


                self.hw.OperationalVacuum = True
                while True:
                    while True:
                        time.sleep(1)
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

                    if "Operational Vacuum" in self.state:
                        self.hw.OperationalVacuum = True
                    else:
                        # #TODO: If you are in debugging mode, you can run as if you were in vacuum (take this out for last testing)
                        self.hw.OperationalVacuum = False

                    Logging.logEvent("Debug","Status Update", 
                    {"message": "Current chamber state: {}".format(self.state),
                     "level": 3})

                    # sleep until the next time around
                    time.sleep(self.updatePeriod)

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

    def state_02(self):  # PullingVac: Start
        if (self.profile.vacuumWanted is True) and \
                (self.roughPumpPressure < 70):
            self.state = 'PullingVac: RoughingCryoP'
            self.hw.Shi_MCC_Cmds.append(['Open_RoughingValve'])
        # Todo: Add vacuum not wanted state move.

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

    def state_05(self):  # PullingVac: Cryo Pumping Chamber
        if (self.chamberPressure < self.pres_opVac):
            self.state = 'Operational Vacuum'
        # Todo: Add vacuum not wanted state move.

    def state_06(self):  # Operational Vacuum: Cryo Pumping
        if self.chamberPressure > self.pres_opVac:
            self.state = 'Non-Operational High Vacuum'
        elif self.hw.ShiCryopump.is_cryopump_cold():
            self.state = 'Operational Vacuum'
            self.hw.PC_104.digital_out.update({'CryoP GateValve': False})

    def state_07(self):  # Operational Vacuum
        if self.chamberPressure > self.pres_opVac:
            self.state = 'Non-Operational High Vacuum'
        elif (not self.hw.ShiCryopump.is_cryopump_cold()) and \
                (self.cryoPumpPressure < self.chamberPressure) and \
                (not self.hw.ShiCryopump.is_regen_active()):
            self.state = 'Operational Vacuum: Cryo Pumping'
            self.hw.PC_104.digital_out.update({'CryoP GateValve': True})
            time.sleep(5)
        else:
            self.hw.PC_104.digital_out.update({'CryoP GateValve': False})

    def state_08(self):  # Non-Operational High Vacuum
        pass

    def wait_for_hardware(self):
        ready = True
        ready &= self.hw.PC_104.digital_in.getVal('CryoP_GV_Open') is not None
        ready &= self.hw.PC_104.digital_in.getVal('CryoP_GV_Open_WF') is not None
        ready &= self.hw.PC_104.digital_in.getVal('CryoP_GV_Closed') is not None
        ready &= self.hw.PC_104.digital_in.getVal('CryoP_GV_Closed_WF') is not None
        ready &= self.hw.PC_104.digital_in.getVal('RoughP_Powered') is not None
        ready &= self.hw.PC_104.digital_in.getVal('RoughP_Powered_WF') is not None
        ready &= self.hw.PC_104.digital_in.getVal('RoughP_On_Sw') is not None
        ready &= self.hw.PC_104.digital_in.getVal('RoughP_On_Sw_WF') is not None
        ready &= self.hw.PfeifferGuages.get_roughpump_pressure() is not None
        ready &= self.hw.PfeifferGuages.get_chamber_pressure() is not None
        ready &= self.hw.PfeifferGuages.get_cryopump_pressure() is not None
        ready &= self.hw.ShiCryopump.is_cryopump_cold() is not None
        ready &= self.hw.ShiCryopump.get_mcc_params('Elapsed Time') is not None
        ready &= self.hw.ShiCryopump.get_mcc_params('Tc Pressure State') is not None
        ready &= self.hw.ShiCryopump.get_mcc_status('Stage 1 Temp') is not None
        ready &= self.hw.ShiCryopump.get_mcc_status('Stage 2 Temp') is not None
        ready &= self.hw.ShiCryopump.get_compressor('Helium Discharge Temperature') is not None
        ready &= self.hw.ShiCryopump.get_compressor('Water Outlet Temperature') is not None
        ready &= self.hw.ShiCryopump.get_compressor('System ON') is not None
        if os.name == "posix":
            userName = os.environ['LOGNAME']
        else:
            userName = "user"
        if not ready and "root" in userName:
            out = "CryoP_GV_Open: {}\n".format(self.hw.PC_104.digital_in.getVal('CryoP_GV_Open'))
            out += "RoughP_Powered: {}\n".format(self.hw.PC_104.digital_in.getVal('RoughP_Powered'))
            out += "RoughP_Powered_WF: {}\n".format(self.hw.PC_104.digital_in.getVal('RoughP_Powered_WF'))
            out += "RoughP_On_Sw: {}\n".format(self.hw.PC_104.digital_in.getVal('RoughP_On_Sw'))
            out += "RoughP_On_Sw_WF: {}\n".format(self.hw.PC_104.digital_in.getVal('RoughP_On_Sw_WF'))
            out += "get_roughpump_pressure: {}\n".format(self.hw.PfeifferGuages.get_roughpump_pressure())
            out += "get_chamber_pressure: {}\n".format(self.hw.PfeifferGuages.get_chamber_pressure())
            out += "get_cryopump_pressure: {}\n".format(self.hw.PfeifferGuages.get_cryopump_pressure())
            out += "Elapsed Time: {}\n".format(self.hw.ShiCryopump.get_mcc_params('Elapsed Time'))
            out += "Tc Pressure State: {}\n".format(self.hw.ShiCryopump.get_mcc_params('Tc Pressure State'))
            out += "Stage 1 Temp: {}\n".format(self.hw.ShiCryopump.get_mcc_status('Stage 1 Temp'))
            out += "Stage 2 Temp: {}\n".format(self.hw.ShiCryopump.get_mcc_status('Stage 2 Temp'))
            out += "Helium Discharge Temperature: {}\n".format(self.hw.ShiCryopump.get_compressor('Helium Discharge Temperature'))
            out += "Water Outlet Temperature: {}\n".format(self.hw.ShiCryopump.get_compressor('Water Outlet Temperature'))
            out += "System ON: {}\n".format(self.hw.ShiCryopump.get_compressor('System ON'))
            Logging.debugPrint(3, out)
        return ready

    def determin_current_vacuum_state(self):
        if (self.chamberPressure < self.pres_opVac):  ##
            return 'Operational Vacuum'
        else:
            return 'Atm: Sys Ready'

    # TODO: Write a wrapper around opening valves to make one final check of the pressures before we open them
