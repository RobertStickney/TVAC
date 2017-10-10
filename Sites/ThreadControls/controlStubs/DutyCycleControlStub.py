from threading import Thread
import json
import uuid
import time
import datetime
import sys
import os
import traceback

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
        self.zoneUUID = uuid.uuid4()
        self.zoneProfile.update(json.loads('{"zoneuuid":"%s"}'%self.zoneUUID))

        self.lamps = lamps
        self.name = name
        self.parent = parent

        self.pid = PID()
        proportional_gain = .2
        integral_gain = 0
        derivative_gain = 0
        self.pid.setKp(proportional_gain)
        self.pid.setKi(integral_gain)
        self.pid.setKd(derivative_gain)

        self.maxTempRisePerMin = 6.4
        self.maxTempRisePerUpdate = (self.maxTempRisePerMin/60)*parent.updatePeriod
    # end init

    def updateDutyCycle(self):
        '''
        Given that temp_temperture is assigned to a value, this will 
        update the duty cycle for the lamps
        '''

        self.pid.SetPoint = self.temp_temperture
        # TODO: Don't leave this hardcoded
        self.pid.update(self.zoneProfile.getTemp("Max"))
        self.dutyCycle = self.pid.error_value/self.maxTempRisePerUpdate

        # TODO: pick what lamp you want to use
        self.parent.d_out.update({self.lamps[1] + " PWM DC": self.dutyCycle})
        self.parent.d_out.update({self.lamps[0] + " PWM DC": self.dutyCycle})

        Logging.logEvent("Debug","Status Update", 
            {"message": "{}: Temp Goal Temperture is {}".format(self.name,self.temp_temperture),
            "level":2})
        Logging.logEvent("Debug","Status Update", 
            {"message": "{}: Current duty Cycle: {}".format(self.name,self.dutyCycle),
            "level":2})
        Logging.logEvent("Event","Expected Temp Update",
        {"expected_temp_values": [self.temp_temperture],
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
        {"message": "Creating Expected temperture values: {}".format(self.name),
         "level":2})
        intervalTime = self.parent.updatePeriod
        # if given a startTime, use that, otherwise, use current
        if startTime:
            if "datetime.datetime" in str(type(startTime)):
                startTime = time.mktime(startTime.timetuple())
            currentTime = int(startTime)
        else:
            currentTime = int(time.time())
        
        # TODO: Change don't let this be hardcoded to Max
        currentTemp = self.zoneProfile.getTemp("Max")

        expected_temp_values = []
        expected_time_values = []
        self.setpoint_ramp_start_time = []
        self.setpoint_soak_start_time = []
        for setPoint in setPoints:
            # get values out from setpoint
            goalTemp = setPoint.tempGoal
            rampTime = setPoint.ramp
            soakTime = setPoint.soakduration
            # skip ramp section if rampTime == 0
            if rampTime:
                TempDelta = goalTemp-currentTemp
                numberOfJumps = rampTime/intervalTime
                intervalTemp = TempDelta/numberOfJumps
                rampEndTime = currentTime+rampTime

                # Debug prints
                debugStatus = {
                "goal Temperture":goalTemp,
                "Time at Start of Setpoint": currentTime,
                "Ramp Duration": rampTime,
                "Delta temp per Update": intervalTemp,
                "Update Time" : self.parent.updatePeriod,
                "TempDelta Total": TempDelta,
                }
                Logging.logEvent("Debug","Data Dump", 
                    {"message": "Setpoint {}: Ramp Status".format(setPoint.thermalsetpoint),
                     "level":3,
                     "dict":debugStatus})

                # setting all values all for ramp
                for i, tempSetPoint in enumerate(range(currentTime,rampEndTime, intervalTime)):
                    x = tempSetPoint
                    y = currentTemp + (i*intervalTemp)
                    expected_time_values.append(tempSetPoint)
                    expected_temp_values.append(y)
            else:
                rampEndTime = currentTime
            self.setpoint_ramp_start_time.append(currentTime)

            # Debug prints
            debugStatus = {
            "Soak Duration": soakTime,
            "goal Temperture":goalTemp,
            }
            Logging.logEvent("Debug","Data Dump", 
                {"message": "Setpoint {}: Soak Status".format(setPoint.thermalsetpoint),
                 "level":3,
                 "dict":debugStatus})

            #Setting all soak values
            self.setpoint_soak_start_time.append(rampEndTime)
            for tempSetPoint in range(rampEndTime, rampEndTime+soakTime, intervalTime):
                x = tempSetPoint
                y = goalTemp
                expected_time_values.append(tempSetPoint)
                expected_temp_values.append(y)
                # print("{},{}".format(x,y))

            # input("pause")

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

        self.paused = False
        self.held   = False




    def run(self):
        # While true to restart the thread if it errors out
        while True:
            # Check to make sure there is an active profile
            # and that we are sitting in an operational vacuum
            # and that all drivers and updaters are running
            if ProfileInstance.getInstance().activeProfile and HardwareStatusInstance.getInstance().OperationalVacuum:
                try:
                    Logging.logEvent("Debug","Status Update", 
                    {"message": "Running Duty Cycle thread",
                     "level":2})
         
                    Logging.logEvent("Event","Start Profile", 
                        {'time': datetime.time(),
                        "ProfileInstance": ProfileInstance.getInstance()})

                    # local temp variables for checking state
                    self.startTime = int(time.time())
                    # Generate the expected values at a given time
                    for zone in self.zones:
                        if self.zones[zone].zoneProfile.activeZoneProfile:
                            self.zones[zone].expected_temp_values, self.expected_time_values = self.zones[zone].createExpectedValues(self.zones[zone].zoneProfile.thermalProfiles, startTime=self.zoneProfiles.startTime)
                    justChangedSetpoint = True
                    # Program loop is here
                    while ProfileInstance.getInstance().activeProfile:

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
                        while currentTime > self.expected_time_values[0]:
                            print("zone1: {}".format(len(self.zones["zone1"].expected_temp_values)))
                            print("zone2: {}".format(len(self.zones["zone2"].expected_temp_values)))
                            print("zone3: {}".format(len(self.zones["zone3"].expected_temp_values)))
                            for zone in self.zones:
                                if self.zones[zone].zoneProfile.activeZoneProfile:
                                    self.zones[zone].temp_temperture = self.zones[zone].expected_temp_values[0]
                                    self.zones[zone].expected_temp_values = self.zones[zone].expected_temp_values[1:]
                            self.expected_time_values = self.expected_time_values[1:]

                            if len(self.expected_time_values) <= 0:
                                break
                            print("{} -- {}".format(currentTime, self.expected_time_values[0]))
                        # With the temp goal tempurture picked, make the duty cycle 
                        for zone in self.zones:
                            if self.zones[zone].zoneProfile.activeZoneProfile:
                                self.zones[zone].updateDutyCycle()

                        # Logging.debugPrint(3,"len expected_time_values:{}".format(len(expected_time_values)) 
                        # if currentTime > self.setpoint_ramp_start_time[self.setpoint]:
                        #     if justChangedSetpoint: 
                        #         justChangedSetpoint = False
                        #         print("Starting ramp for setpoint: {} at time {}".format(self.setpoint,time.time()))

                        # if currentTime > self.setpoint_soak_start_time[self.setpoint]:
                        #     print("Starting Soak for setpoint: {} at time {}".format(self.setpoint,time.time()))
                        #     self.setpoint += 1
                        #     justChangedSetpoint = True

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
                            self.d_out.update({zone.lamps[1] + " PWM DC": 0})
                            self.d_out.update({zone.lamps[0] + " PWM DC": 0})

                    #TODO: Turn on the heaters here

                    Logging.logEvent("Event","End Profile", 
                        {'time': datetime.time(),
                        "ProfileInstance": ProfileInstance.getInstance()})

                    self.updateDBwithEndTime()
                    self.running = False
                    # self.zoneProfile.activeZoneProfile = False
                    # This assumes all zones have the same end time
                    ProfileInstance.getInstance().activeProfile = False
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print("Error: {} in file {}:{}".format(exc_type, fname, exc_tb.tb_lineno))

                    # FileCreation.pushFile("Error",self.zoneUUID,'{"errorMessage":"%s"}'%(e))
                    self.running = False
                    ProfileInstance.getInstance().zoneProfiles.activeProfile = False
                    raise e
                # end of try, catch
            # Sleeping so it doesn't busty wait
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
            raise e


    def checkHold(self):
        '''
        This is a helper function that keeps the loop held in same temp.
        It recreates the expected values with updated times at the end

        TODO: NOTE: if a hold is held less than updateTime it might not recalculate or even get in here
        '''


        try:
            if self.held:
                startHoldTime = int(time.time())

                Logging.logEvent("Event","Hold Start", 
                {"message": "In hold for first time",
                "level":3})
                while self.held:
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
            Logging.logEvent("Debug","Status Update", 
            {"message": "hold error: {}".format("\n".join(traceback.format_list(traceback.extract_stack()))),
            "level":3})
            raise e

    def checkPause(self):
        '''
        This is a helper function that pauses the loop
        '''
        try:
            if self.paused:
                startPauseTime = int(time.time())
                Logging.logEvent("Event","Hold Start", 
                    {"message": "In hold for first time",
                    "level":3})
                while self.paused:
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
            Logging.logEvent("Debug","Status Update", 
            {"message": "pause error: {}".format("\n".join(traceback.format_list(traceback.extract_stack()))),
            "level":3})
            raise e


