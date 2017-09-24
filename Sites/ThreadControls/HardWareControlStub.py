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
    This class contains the main inteligences for reading the data from the system,
    and telling the lamps what to do. 

    It controls if we are in a ramp, hold, soak, or paused.
    It also generates the expected temp values at the given time 
    '''


    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None, lamps=None):

        Logging.logEvent("Debug","Status Update", 
        {"message": "Creating HardWareControlStub: {}".format(args[0]),
         "level":3})

        Thread.__init__(self, group=group, target=target, name=name)
        self.args = args
        self.kwargs = kwargs

        self.zoneProfiles = ProfileInstance.getInstance().zoneProfiles
        self.zoneProfile = self.zoneProfiles.getZone(self.args[0])
        self.updatePeriod = self.zoneProfiles.updatePeriod
        self.d_out = HardwareStatusInstance.getInstance().PC_104.digital_out

        self.running = False
        self.paused = False
        self.inHold = False
        self.zoneUUID = uuid.uuid4()
        self.zoneProfile.update(json.loads('{"zoneuuid":"%s"}'%self.zoneUUID))
        self.timeStartForHold = None
        self.lamps = lamps

        self.tempGoalTemperature = 0
        self.pid = PID()

        self.maxTempRisePerMin = 10
        self.maxTempRisePerUpdate = (self.maxTempRisePerMin/60)*self.updatePeriod


    def createExpectedValues(self, setPoints,startTime=None):
        '''
        This is a helper function that given a list of setpoints
        containing a GoalTemp, RampTime and SoakTime. It will 
        generate a list time values and matching temputure values
        '''
        Logging.logEvent("Debug","Status Update", 
        {"message": "Creating Expected temperture values: {}".format(self.args[0]),
         "level":2})
        intervalTime = self.updatePeriod
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
                "Update Time" : self.updatePeriod,
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


            currentTime = rampEndTime+soakTime
            currentTemp = goalTemp
        # end of for loop, end generating outputs


        return expected_temp_values, expected_time_values


    def run(self):
        # Always run this thread
        while True:
            # Check to make sure there is an active profile
            # and that we are sitting in an operational vacuum
            if ProfileInstance.getInstance().activeProfile and HardwareStatusInstance.getInstance().OperationalVacuum:
                try:
                    Logging.logEvent("Debug","Status Update", 
                    {"message": "{}: Running HW control Thread".format(self.args[0]),
                     "level":2})
         
                    Logging.logEvent("Event","Start Profile", 
                        {'time': datetime.time()})

                    # Setup code is here

                    self.updatePeriod = 10
                    self.maxTempRisePerMin = 6.4
                    self.setpoint = 0
                    self.maxTempRisePerUpdate = (self.maxTempRisePerMin/60)*self.updatePeriod

                    self.pid = PID()
                    proportional_gain = .2
                    integral_gain = 0
                    derivative_gain = 0
                    self.pid.setKp(proportional_gain)
                    self.pid.setKi(integral_gain)
                    self.pid.setKd(derivative_gain)

                    # local temp variables for checking state
                    self.startTime = int(time.time())
                    # Generate the expected values at a given time
                    self.expected_temp_values, self.expected_time_values = self.createExpectedValues(self.zoneProfile.thermalProfiles, startTime=self.zoneProfiles.startTime)
                    justChangedSetpoint = True
                    # Program loop is here
                    while True:

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
                            self.temp_temperture = self.expected_temp_values[0]
                            self.expected_temp_values = self.expected_temp_values[1:]
                            self.expected_time_values = self.expected_time_values[1:]

                            if len(self.expected_time_values) <= 0:
                                break
                        # With the temp goal tempurture picked, make the duty cycle 
                        self.updateDutyCycle()

                        if currentTime > self.setpoint_ramp_start_time[self.setpoint]:
                            if justChangedSetpoint: 
                                justChangedSetpoint = False
                                print("Starting ramp for setpoint: {} at time {}".format(self.setpoint,time.time()))

                        if currentTime > self.setpoint_soak_start_time[self.setpoint]:
                            print("Starting Soak for setpoint: {} at time {}".format(self.setpoint,time.time()))
                            self.setpoint += 1
                            justChangedSetpoint = True

                        if len(self.expected_time_values) <= 0:
                            break
                        # sleep until the next time around
                        time.sleep(self.updatePeriod)
                    # end of inner while True
                    # end of test

                    # turning off lamps at the end of test
                    self.d_out.update({self.lamps[1] + " PWM DC": 0})
                    self.d_out.update({self.lamps[0] + " PWM DC": 0})

                    #TODO: Turn on the heaters here

                    Logging.logEvent("Event","End Profile", 
                        {'time': datetime.time()})

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

    def updateDutyCycle(self):
        '''
        Given that temp_temperture is assigned to a value, this will 
        update the duty cycle for the lamps
        '''

        Logging.logEvent("Debug","Status Update", 
            {"message": "{}: Temp Goal Temperture is {}".format(self.args[0],self.temp_temperture),
            "level":2})
        self.pid.SetPoint = self.temp_temperture
        # TODO: Don't leave this hardcoded
        self.pid.update(self.zoneProfile.getTemp("Max"))
        self.dutyCycle = self.pid.error_value/self.maxTempRisePerUpdate

        # TODO: pick what lamp you want to use
        self.d_out.update({self.lamps[1] + " PWM DC": self.dutyCycle})
        self.d_out.update({self.lamps[0] + " PWM DC": self.dutyCycle})

        Logging.logEvent("Event","Expected Temp Update",
        {"expected_temp_values": [self.temp_temperture],
         "expected_time_values": [time.time()],
         "zone"                : self.args[0],
         "profileUUID"         : self.zoneProfile.profileUUID,
        })



    def checkHold(self):
        '''
        This is a helper function that keeps the loop held in same temp.
        It recreates the expected values with updated times at the end

        TODO: NOTE: if a hold is held less than updateTime it might not recalculate or even get in here
        '''
        if self.inHold:
            inHoldFlag = True
            self.event('hold')
            startHoldTime = int(time.time())
            print("in hold for first time")
        else:
            inHoldFlag = False
        while self.inHold:
            self.updateDutyCycle()
            time.sleep(.5)
        if inHoldFlag:
            endHoldTime = int(time.time())
            holdTime = endHoldTime - startHoldTime
            self.startTime = self.startTime + holdTime
            # regenerate expected time, moving things forward to account for hold
            self.expected_temp_values, self.expected_time_values = self.createExpectedValues(self.zoneProfile.thermalProfiles, startTime=self.startTime)
            inHoldFlag = False

    def checkPause(self):
        '''
        This is a helper function that pauses the loop
        '''
        if self.paused:
            inPause = True
            # turn off lamps while paused
            self.d_out.update({self.lamps[1] + " PWM DC": 0})
            self.d_out.update({self.lamps[0] + " PWM DC": 0})
            self.event('pause')
        else:
            inPause = False
        while self.paused:
            time.sleep(.5)
        if inPause:
            inPause = False
            self.event('endpause')

    def event(self,eventName):
        # TODO: Remove this and make all calls to this go to Logging.Logevent()
        return {}
