from threading import Thread
import json
import uuid
import time
import datetime
import sys
import os
import traceback
import math

from Collections.ProfileInstance import ProfileInstance
from Collections.HardwareStatusInstance import HardwareStatusInstance
from PID.PID import PID

from Logging.MySql import MySQlConnect
from Logging.Logging import Logging

class ZoneControlStub():
    def __init__(self, name, lamps=None, parent=None):
        Logging.logEvent("Debug","Status Update", 
        {"message": "Creating ZoneControlStub: {}".format(name),
         "level":3})


        self.zoneProfile = ProfileInstance.getInstance().zoneProfiles.getZone(name)

        self.lamps = lamps
        self.name = name
        self.parent = parent
        self.temp_temperature = None

        self.pid = PID()
        if lamps:
            # These are the PID settings for the lamps
            proportional_gain = .2
            integral_gain = 0
            derivative_gain = 0
        else:
            # These are the PID settings for the heaters in the platen
            proportional_gain = .4
            integral_gain = 0
            derivative_gain = 0

        self.pid.setKp(proportional_gain)
        self.pid.setKi(integral_gain)
        self.pid.setKd(derivative_gain)


    # end init

    def updateDutyCycle(self):
        '''
        Given that temp_temperature is assigned to a value, this will 
        update the duty cycle for the lamps
        '''

        self.pid.SetPoint = self.temp_temperature
        # TODO: Don't leave this hardcoded
        self.pid.update(self.zoneProfile.getTemp(self.zoneProfile.average))
        self.dutyCycle = self.pid.error_value/self.maxTempRisePerUpdate

        # TODO: pick what lamp you want to use
        if self.lamps:
            self.parent.d_out.update({self.lamps[1] + " PWM DC": self.dutyCycle})
            self.parent.d_out.update({self.lamps[0] + " PWM DC": self.dutyCycle})
        else:
            # for zone 9, the platen
            HardwareStatusInstance.getInstance().TdkLambda_Cmds.append(['Platen Duty Cycle', self.dutyCycle])

        Logging.debugPrint(2, "{}: avg ({})\goal({}) -- {}".format(self.name,
                                                    self.zoneProfile.getTemp(self.zoneProfile.average),
                                                    self.temp_temperature,
                                                    self.dutyCycle))
        # Logging.logEvent("Debug","Status Update", 
        #     {"message": "{}: Current temp: {}".format(self.name,self.zoneProfile.getTemp(self.zoneProfile.average)),
        #     "level":2})
        # Logging.logEvent("Debug","Status Update", 
        #     {"message": "{}: Temp Goal temperature is {}".format(self.name,self.temp_temperature),
        #     "level":2})
        # Logging.logEvent("Debug","Status Update", 
        #     {"message": "{}: Current duty Cycle: {}".format(self.name,self.dutyCycle),
        #     "level":2})
        Logging.logExpectedTemperatureData(
        {"expected_temp_values": [self.temp_temperature],
         "expected_time_values": [time.time()],
         "zone"                : self.name,
         "profileUUID"         : self.zoneProfile.profileUUID,
         "ProfileInstance"     : ProfileInstance.getInstance()
        })

    def createExpectedValues(self, setPoints,startTime=None):
        '''
        This is a helper function that given a list of setpoints
        containing a GoalTemp, RampTime and SoakTime. It will 
        generate a list time values and matching temputure values
        '''
        Logging.logEvent("Debug","Status Update", 
        {"message": "DCCS: Creating Expected temperature values: {}".format(self.name),
         "level":2})
        intervalTime = self.parent.updatePeriod
        # if given a startTime, use that, otherwise, use current
        Logging.debugPrint(1,"DCCS: thermalStartTime: {}".format(self.parent.zoneProfiles.thermalStartTime))
        if startTime:
            Logging.debugPrint(3,"DCCS: Starttime is: {}\t current: {}".format(startTime, time.time()))
            if "datetime.datetime" in str(type(startTime)):
                startTime = time.mktime(startTime.timetuple())
            currentTime = int(startTime)
        else:
            currentTime = int(time.time())

        # This loop is to hold the program here until the temperature vaules have been loaded
        if os.name == 'posix':
            userName = os.environ['LOGNAME']
        else:
            userName = "User"
        if "root" in userName:
            while True:
                currentTemp = self.zoneProfile.getTemp(self.zoneProfile.average)
                Logging.debugPrint(1,"DCCS: currentTemp: {}".format(currentTemp))
                if not math.isnan(currentTemp) and int(currentTemp) != 0:
                    break
                time.sleep(.5)
        else:
            currentTemp = self.zoneProfile.getTemp(self.zoneProfile.average)

        expected_temp_values = []
        expected_time_values = []
        self.parent.setpoint_start_time = []
        for setPoint in setPoints:
            # get values out from setpoint
            goalTemp = setPoint.tempGoal
            rampTime = setPoint.ramp
            soakTime = setPoint.soakduration
            currentTime2 = time.time()
            # skip ramp section if rampTime == 0
            if rampTime:
                TempDelta = goalTemp-currentTemp
                numberOfJumps = rampTime/intervalTime
                intervalTemp = TempDelta/numberOfJumps
                rampEndTime = currentTime+rampTime

                # Debug prints
                debugStatus = {
                "goal temperature":goalTemp,
                "Time at Start of Setpoint": currentTime,
                "Ramp Duration": rampTime,
                "Delta temp per Update": intervalTemp,
                "Update Time" : self.parent.updatePeriod,
                "TempDelta Total": TempDelta,
                }
                Logging.logEvent("Debug","Data Dump", 
                    {"message": "DCCS: Setpoint {}: Ramp Status".format(setPoint.thermalsetpoint),
                     "level":3,
                     "dict":debugStatus})

                # setting all values all for ramp
                notUsed = 0
                for i, tempSetPoint in enumerate(range(currentTime,rampEndTime, intervalTime)):
                    if tempSetPoint > currentTime2:
                        x = tempSetPoint
                        y = currentTemp + ((i-notUsed)*intervalTemp)
                        expected_time_values.append(tempSetPoint)
                        expected_temp_values.append(y)
                    else:
                        notUsed += 1
            else:
                rampEndTime = currentTime
            self.parent.setpoint_start_time.append([currentTime,0])

            # Debug prints
            debugStatus = {
            "Soak Duration": soakTime,
            "goal temperature":goalTemp,
            }
            Logging.logEvent("Debug","Data Dump", 
                {"message": "DCCS: Setpoint {}: Soak Status".format(setPoint.thermalsetpoint),
                 "level":3,
                 "dict":debugStatus})

            #Setting all soak values
            self.parent.setpoint_start_time[-1][1] = rampEndTime
            for tempSetPoint in range(rampEndTime, rampEndTime+soakTime, intervalTime):
                if tempSetPoint > currentTime2:
                    x = tempSetPoint
                    y = goalTemp
                    expected_time_values.append(tempSetPoint)
                    expected_temp_values.append(y)
            currentTime = rampEndTime+soakTime
            currentTemp = goalTemp
        # end of for loop, end generating outputs

       # print("Logging all data")
       # Logging.logEvent("Event","Expected Temp Update",
       # {"expected_temp_values": expected_temp_values,
       #  "expected_time_values": expected_time_values,
       #  "zone"                : self.args[0],
       #  "profileUUID"         : self.zoneProfile.profileUUID,
       #  "ProfileInstance"     : ProfileInstance.getInstance()
       # })


        return expected_temp_values, expected_time_values

class DutyCycleControlStub(Thread):
    '''
    This class contains the main inteligences for reading the data from the system,
    and telling the lamps what to do. 

    It controls if we are in a ramp, hold, soak, or paused.
    It also generates the expected temp values at the given time 
    '''

    def __init__(self):
        Logging.logEvent("Debug","Status Update", 
        {"message": "Creating DutyCycleControlStub",
         "level":2})

        self.zoneProfiles = ProfileInstance.getInstance().zoneProfiles

        Thread.__init__(self)
        self.updatePeriod = ProfileInstance.getInstance().zoneProfiles.updatePeriod
        self.d_out        = HardwareStatusInstance.getInstance().PC_104.digital_out

        self.zones = {
            "zone1": ZoneControlStub(name='zone1',lamps=['IR Lamp 1','IR Lamp 2'], parent=self),
            "zone2": ZoneControlStub(name='zone2',lamps=['IR Lamp 3','IR Lamp 4'], parent=self),
            "zone3": ZoneControlStub(name='zone3',lamps=['IR Lamp 6','IR Lamp 5'], parent=self),
            "zone4": ZoneControlStub(name='zone4',lamps=['IR Lamp 7','IR Lamp 8'], parent=self),
            "zone5": ZoneControlStub(name='zone5',lamps=['IR Lamp 9','IR Lamp 10'], parent=self),
            "zone6": ZoneControlStub(name='zone6',lamps=['IR Lamp 12','IR Lamp 11'], parent=self),
            "zone7": ZoneControlStub(name='zone7',lamps=['IR Lamp 13','IR Lamp 14'], parent=self),
            "zone8": ZoneControlStub(name='zone8',lamps=['IR Lamp 15','IR Lamp 16'], parent=self),
            # zone9 is the platen
            "zone9": ZoneControlStub(name='zone9', parent=self)
            }


        self.currentSetpoint = 1
        self.ramp = False
        self.soak = False




    def run(self):
        # While true to restart the thread if it errors out
        while True:
            # Check to make sure there is an active profile
            # and that we are sitting in an operational vacuum
            # and that all drivers and updaters are running
            if ProfileInstance.getInstance().activeProfile and \
                HardwareStatusInstance.getInstance().OperationalVacuum and \
                ProfileInstance.getInstance().zoneProfiles.getActiveProfileStatus():
                try:
                    Logging.logEvent("Debug","Status Update", 
                    {"message": "DCCS: Starting Duty Cycle thread",
                     "level":2})
                    
                    Logging.logEvent("Event","Start Profile", 
                        {'time': datetime.time(),
                        "message":ProfileInstance.getInstance().zoneProfiles.profileName,
                        "ProfileInstance": ProfileInstance.getInstance()})


                    ProfileInstance.getInstance().zoneProfiles.updateThermalStartTime(time.time())

                    # local temp variables for checking state
                    #TODO: Start time should gotten somewhere else, not made here
                    if self.zoneProfiles.thermalStartTime:
                        self.startTime = self.zoneProfiles.thermalStartTime
                    else:
                        self.startTime = int(time.time())
                    currentSetpointTemporary = 1
                    rampTemporary = False
                    soakTemporary = True


                    Logging.logEvent("Debug","Status Update", 
                    {"message": "DCCS: Setting up Platen",
                     "level":2})
                    HardwareStatusInstance.getInstance().TdkLambda_Cmds.append(['Setup Platen', ''])

                    for zone in self.zones:
                        if self.zones[zone].zoneProfile.activeZoneProfile:
                            self.zones[zone].maxTempRisePerMin = self.zones[zone].zoneProfile.maxHeatPerMin
                            self.zones[zone].maxTempRisePerUpdate = (self.zones[zone].maxTempRisePerMin/60)*self.updatePeriod
                            self.zones[zone].expected_temp_values, self.expected_time_values = self.zones[zone].createExpectedValues(self.zones[zone].zoneProfile.thermalProfiles, startTime=self.zoneProfiles.thermalStartTime)
                    # Program loop is here
                    while ProfileInstance.getInstance().activeProfile:

                        Logging.logEvent("Debug","Status Update", 
                            {"message": "DCCS: Running Duty Cycle Thread",
                             "level":3})

                        # You might need to stay is pause
                        self.checkPause()
                        self.checkHold()

                        # get current time
                        currentTime = time.time()
 
                        # if there is no more expected time values, break out of while True loop
                        if len(self.expected_time_values) <= 0:
                            break


                        # this will find the time value matching the current time
                        # and give us the temp value it should be at that time.
                        # print("currentTime: {}".format(currentTime))
                        # print("expected_time_values: {}".format(self.expected_time_values))
                        while currentTime > self.expected_time_values[0]:

                            for zone in self.zones:
                                if self.zones[zone].zoneProfile.activeZoneProfile:
                                    self.zones[zone].temp_temperature = self.zones[zone].expected_temp_values[0]
                                    self.zones[zone].expected_temp_values = self.zones[zone].expected_temp_values[1:]
                            self.expected_time_values = self.expected_time_values[1:]
                            if len(self.setpoint_start_time) > 0:
                                if currentTime > self.setpoint_start_time[0][0]:
                                    rampTemporary = True
                                    soakTemporary = False
                                    if currentTime > self.setpoint_start_time[0][1]:
                                        rampTemporary = False
                                        soakTemporary = True
                                        self.setpoint_start_time = self.setpoint_start_time[1:]
                                        currentSetpointTemporary += 1
                                    if len(self.setpoint_start_time) <= 0:
                                        break

                            if len(self.expected_time_values) <= 0:
                                break

                        # compare the temps just made with the values in self.
                        # if they are different, or important log it
                        if rampTemporary == True and self.ramp == False:
                            ProfileInstance.getInstance().currentSetpoint = currentSetpointTemporary
                            Logging.logEvent("Event","Profile",
                                {"message":"Profile {} has entered setpoint {} Ramp".format(ProfileInstance.getInstance().zoneProfiles.profileName, currentSetpointTemporary),
                                "ProfileInstance": ProfileInstance.getInstance()})
                        if soakTemporary == True and self.soak == False:
                            if currentSetpointTemporary > 1:
                                Logging.logEvent("Event","Profile",
                                    {"message":"Profile {} has entered setpoint {} Soak".format(ProfileInstance.getInstance().zoneProfiles.profileName, currentSetpointTemporary-1),
                                    "ProfileInstance": ProfileInstance.getInstance()})
                                ProfileInstance.getInstance.inRamp = False
                        self.ramp = rampTemporary
                        self.soak = soakTemporary
                        # With the temp goal tempurture picked, make the duty cycle 
                        for zone in self.zones:
                            if self.zones[zone].zoneProfile.activeZoneProfile:
                                # This checks to see if a current temp has been made...
                                if self.zones[zone].temp_temperature:
                                    self.zones[zone].updateDutyCycle()
                                else:
                                    print("Waiting...")

                            if len(self.expected_time_values) <= 0:
                                break
                        # sleep until the next time around
                        time.sleep(self.updatePeriod)
                    # end of inner while True
                    # end of test

                    # turning off lamps at the end of test

                    for zone in self.zones:
                        if self.zones[zone].zoneProfile.activeZoneProfile:

                            zone = self.zones[zone]
                            if zone.lamps:
                                self.d_out.update({zone.lamps[1] + " PWM DC": 0})
                                self.d_out.update({zone.lamps[0] + " PWM DC": 0})
                            else:
                                HardwareStatusInstance.getInstance().TdkLambda_Cmds.append(['Platen Duty Cycle', 0])
                    #TODO: Turn off the heaters here

                    Logging.logEvent("Event","End Profile", 
                        {'time': datetime.time(),
                        "message":ProfileInstance.getInstance().zoneProfiles.profileName,
                        "ProfileInstance": ProfileInstance.getInstance()})

                    HardwareStatusInstance.getInstance().TdkLambda_Cmds.append(['Disable Platen Output',''])

                    self.updateDBwithEndTime()
                    self.running = False
                    tcList = HardwareStatusInstance.getInstance().Thermocouples.tcList
                    for tc in tcList:
                        tc.update({"zone":0,"userDefined":False})



                    # self.zoneProfile.activeZoneProfile = False
                    # This assumes all zones have the same end time
                    ProfileInstance.getInstance().activeProfile = False
                    ProfileInstance.getInstance().vacuumWanted = False
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print("Error: {} in file {}:{}".format(exc_type, fname, exc_tb.tb_lineno))

                    # FileCreation.pushFile("Error",self.zoneUUID,'{"errorMessage":"%s"}'%(e))
                    self.running = False
                    ProfileInstance.getInstance().zoneProfiles.activeProfile = False
                    Logging.debugPrint(1, "DCCS: Error in run, Duty Cycle: {}".format(str(e)))
                    if Logging.debug:
                        raise e
                # end of try, catch
            else:
                Logging.debugPrint(4,"DCCS: activeProfile: {}".format(ProfileInstance.getInstance().activeProfile))
                Logging.debugPrint(4,"DCCS: OperationalVacuum: {}".format(HardwareStatusInstance.getInstance().OperationalVacuum))
                Logging.debugPrint(4,"DCCS: getActiveProfileStatus: {}".format(ProfileInstance.getInstance().zoneProfiles.getActiveProfileStatus()))
            # Sleeping so it doesn't busy wait
            time.sleep(1)
            # end of running check
        # end of outter while True
    # end of run()

    def updateDBwithEndTime(self):
        sql = "update tvac.Profile_Instance set endTime=\"{}\" where endTime is null;".format(datetime.datetime.fromtimestamp(time.time()))

        mysql = MySQlConnect()
        try:
            mysql.cur.execute(sql)
            mysql.conn.commit()
        except Exception as e:
            Logging.debugPrint(1, "Error in updateDBwithEndTime, Duty Cycle control: {}".format(str(e)))
            if Logging.debug:
                raise e


    def checkHold(self):
        '''
        This is a helper function that keeps the loop held in same temp.
        It recreates the expected values with updated times at the end

        TODO: NOTE: if a hold is held less than updateTime it might not recalculate or even get in here
        '''


        try:
            if ProfileInstance.getInstance().inHold:
                startHoldTime = int(time.time())

                Logging.logEvent("Event","Hold Start", 
                {"message": "In hold for first time",
                "level":3})
                while ProfileInstance.getInstance().inHold:
                    for zone in self.zones:
                        if self.zones[zone].zoneProfile.activeZoneProfile:
                            zone = self.zones[zone]
                            zone.updateDutyCycle()
                    time.sleep(.5)

                endHoldTime = int(time.time())
                holdTime = endHoldTime - startHoldTime
                self.startTime = self.startTime + holdTime
                Logging.logEvent("Event","HoldEnd", 
                {"message": "Just Left hold",
                "level":3})
                Logging.logEvent("Debug","Status Update", 
                {"message": "Leaving hold after {} seconds in hold, new startTime {}".format(holdTime, self.startTime),
                "level":3})
                # regenerate expected time, moving things forward to account for hold
                for zone in self.zones:
                    if self.zones[zone].zoneProfile.activeZoneProfile:
                        self.zones[zone].expected_temp_values, self.expected_time_values = self.zones[zone].createExpectedValues(self.zones[zone].zoneProfile.thermalProfiles, startTime=self.startTime)
        except Exception as e:
            Logging.debugPrint(1, "Error in check Hold, Duty Cycle: {}".format(str(e)))
            if Logging.debug:
                raise e

    def checkPause(self):
        '''
        This is a helper function that pauses the loop
        '''
        try:
            if ProfileInstance.getInstance().inPause:
                startPauseTime = int(time.time())
                Logging.logEvent("Event","Pause Start", 
                    {"message": "In Pause for first time",
                    "level":3})
                while ProfileInstance.getInstance().inPause:
                    for zone in self.zones:
                        if self.zones[zone].zoneProfile.activeZoneProfile:
                            zone = self.zones[zone]
                            self.d_out.update({zone.lamps[1] + " PWM DC": 0})
                            self.d_out.update({zone.lamps[0] + " PWM DC": 0})
                            zone.pid.error_value = 0
                            zone.dutyCycle = 0
                    time.sleep(.5)
                endPauseTime = int(time.time())
                pauseTime = endPauseTime - startPauseTime
                self.startTime = self.startTime + pauseTime
                Logging.logEvent("Event","pauseEnd", 
                {"message": "Just Left pause",
                "level":3})
                Logging.logEvent("Debug","Status Update", 
                {"message": "Leaving pause after {} seconds in pause, new startTime {}".format(pauseTime, self.startTime),
                "level":3})
                # regenerate expected time, moving things forward to account for pause
                for zone in self.zones:
                    if self.zones[zone].zoneProfile.activeZoneProfile:
                        self.zones[zone].expected_temp_values, self.expected_time_values = self.zones[zone].createExpectedValues(self.zones[zone].zoneProfile.thermalProfiles, startTime=self.startTime)
        except Exception as e:
            Logging.debugPrint(1, "Error in check Pause, Duty Cycle Control Stub: {}".format(str(e)))
            if Logging.debug:
                raise e


