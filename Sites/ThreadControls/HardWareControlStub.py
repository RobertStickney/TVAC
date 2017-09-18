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

from Logging.Logging import Logging


class HardWareControlStub(Thread):
    '''
    This class contains the main inteligences for reading the data from the system,
    and telling the lamps what to do. 

    It controls if we are in a ramp, hold, soak, or paused. 
    '''

    def createExpectedValues(self, setPoints,startTime=None):
        intervalTime = self.updatePeriod
        if startTime:
            currentTime = int(startTime)
        else:
            currentTime = int(time.time())
        
        # TODO: Change don't let this be hardcoded to Max
        currentTemp = self.zoneProfile.getTemp("Max")

        expected_temp_values = []
        expected_time_values = []
        for setPoint in setPoints:
            goalTemp = setPoint.tempGoal
            rampTime = setPoint.ramp
            soakTime = setPoint.soakduration
            print("setpoint: {}".format(setPoint.thermalsetpoint))
            print("currentTime: {}".format(currentTime))

            if rampTime:
                TempDelta = goalTemp-currentTemp
                numberOfJumps = rampTime/intervalTime
                intervalTemp = TempDelta/numberOfJumps
                rampEndTime = currentTime+rampTime

                # Debug prints
                print("rampTime: {}".format(rampTime))
                print("TempDelta: {}".format(TempDelta))
                print("numberOfJumps: {}".format(numberOfJumps))
                print("intervalTemp: {}".format(intervalTemp))

                # setting all values all for ramp
                for i, tempSetPoint in enumerate(range(currentTime,rampEndTime, intervalTime)):
                    x = tempSetPoint
                    y = currentTemp + (i*intervalTemp)
                    expected_time_values.append(tempSetPoint)
                    expected_temp_values.append(y)
                    print("{},{}".format(x,y))
            else:
                rampEndTime = currentTime

            print("soakTime: {}".format(soakTime))
            #Setting all soak values
            for tempSetPoint in range(rampEndTime, rampEndTime+soakTime, intervalTime):
                x = tempSetPoint
                y = goalTemp
                expected_time_values.append(tempSetPoint)
                expected_temp_values.append(y)
                print("{},{}".format(x,y))


            currentTime = rampEndTime+soakTime
            currentTemp = goalTemp

        return expected_temp_values, expected_time_values

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None, lamps=None):

        Logging.logEvent("Debug","Status Update", 
        {"message": "Creating HardWareControlStub: {}".format(args[0]),
         "level":3})

        Thread.__init__(self, group=group, target=target, name=name)
        self.args = args
        self.kwargs = kwargs

        profileInstance = ProfileInstance.getInstance()
        self.zoneProfile = profileInstance.zoneProfiles.getZone(self.args[0])
        self.updatePeriod = profileInstance.zoneProfiles.updatePeriod
        self.handeled = False
        self.running = False
        self.paused = False
        self.setPoint = 0
        self.inHold = False
        self.inRamp = True
        self.inSoak = False
        self.soakComplete = False
        self.runCount = 1
        self.tempRampStepCount = 0
        self.tempChange = 0.0
        self.zoneUUID = uuid.uuid4()
        self.zoneProfile.update(json.loads('{"zoneuuid":"%s"}'%self.zoneUUID))
        self.timeStartForHold = None
        self.lamps = lamps

        self.tempGoalTemperature = 0
        self.timerOn = False
        self.pid = PID()

        self.maxTempRisePerMin = 10
        self.maxTempRisePerUpdate = (self.maxTempRisePerMin/60)*self.updatePeriod



    def run(self):
        try:
            Logging.logEvent("Debug","Status Update", 
            {"message": "{}: Running HW control Thread".format(self.args[0]),
             "level":2})
            self.running = True

            

            # self.event('StartRun')
            Logging.logEvent("Event","Start Profile", 
                {'time': datetime.time()})

            currentTemp = self.zoneProfile.getTemp("Max")
            # self.zoneProfile.thermalProfiles[self.setPoint].temp = currentTemp

            d_out = HardwareStatusInstance.getInstance().PC_104.digital_out

            self.updatePeriod = 10
            self.maxTempRisePerMin = 6.4
            self.maxTempRisePerUpdate = (self.maxTempRisePerMin/60)*self.updatePeriod

            self.pid = PID()
            proportional_gain = .2
            integral_gain = 0
            derivative_gain = 0
            self.pid.setKp(proportional_gain)
            self.pid.setKi(integral_gain)
            self.pid.setKd(derivative_gain)

            # local temp variables for checking state
            inHoldFlag = False
            self.startTime = int(time.time())
            # Generate the expected values at a given time
            self.expected_temp_values, self.expected_time_values = self.createExpectedValues(self.zoneProfile.thermalProfiles)

            # continue until we break out
            while True:
                # get current time
                currentTime = time.time()

                while self.inHold:
                    if not inHoldFlag:
                        # first time through hold loop
                        print("in hold for first time")
                        startHoldTime = int(time.time())
                        inHoldFlag = True
                if inHoldFlag:
                    print("Just now leaving hold")
                    endHoldTime = int(time.time())
                    holdTime = endHoldTime - startHoldTime
                    startTime = startTime + holdTime
                    # regenerate expected time, moving things forward to account for hold
                    self.expected_temp_values, self.expected_time_values = self.createExpectedValues(self.zoneProfile.thermalProfiles, startTime=startTime)
                    inHoldFlag = False
                    currentTime = time.time()

                # if there is no more expected time values, break out of while True loop
                if len(self.expected_time_values) <= 0:
                    break

                # this will find the time value matching the current time
                # and give us the temp value it should be at that time. 
                while currentTime > self.expected_time_values[0]:
                    print("At time {} temp should be: {}".format(self.expected_time_values[0],self.expected_temp_values[0]))
                    temp_temp = self.expected_temp_values[0]
                    self.expected_temp_values = self.expected_temp_values[1:]
                    self.expected_time_values = self.expected_time_values[1:]

                    if len(self.expected_time_values) <= 0:
                        break
                # With the temp goal tempurture picked, make the duty cycle 
                self.pid.SetPoint = temp_temp
                # TODO: Don't leave this hardcoded
                self.pid.update(self.zoneProfile.getTemp("Max"))
                self.dutyCycle = self.pid.error_value/self.maxTempRisePerUpdate

                # TODO: pick what lamp you want to use
                d_out.update({self.lamps[1] + " PWM DC": self.dutyCycle})
                d_out.update({self.lamps[0] + " PWM DC": self.dutyCycle})

                # sleep until the next time around
                time.sleep(self.updatePeriod)


            # while self.runCount > 0:

            #     currentTemp = self.zoneProfile.getTemp("Max")
                
            #     self.runProcess()

            #     self.zoneProfile.thermalProfiles[self.setPoint].temp += self.tempChange
            #     self.tempGoalTemperature = self.zoneProfile.thermalProfiles[self.setPoint].temp
            #     self.pid.SetPoint = self.tempGoalTemperature
            #     self.pid.update(currentTemp)
            #     self.dutyCycle = self.pid.error_value/self.maxTempRisePerUpdate
            #     goalTemp = self.zoneProfile.thermalProfiles[self.setPoint].tempGoal
            #     soakduration = self.zoneProfile.thermalProfiles[self.setPoint].soakduration
            #     if self.inRamp:
            #         self.state = "Ramp"
            #     elif self.inSoak:
            #         self.state = "Soak"
            #     else:
            #         self.state = "Other"
            #     status = {
            #         "Soak duration": soakduration,
            #         "Current State": self.state,
            #         "Current Temp": currentTemp,
            #         "Setpoint Goal Temp": goalTemp,
            #         "Temporary Goal Temp": self.tempGoalTemperature,
            #         "Assumed Max Temp Raise per Update": self.maxTempRisePerUpdate,
            #         "Percent of current duty cycle":self.dutyCycle,
            #         "Run Count":self.runCount,
            #         "Set point": self.setPoint
            #     }
            #     Logging.logEvent("Debug","Data Dump", 
            #             {"message": "Current profile Status for {} (in k)".format(self.args[0]),
            #              "level":1,
            #              "dict":status})
            #     # for testing...
            #     print("{}: {} Percent DC".format(self.args[0],self.dutyCycle))
            #     with open('./TempLog.txt','a') as filer:
            #         filer.write("{},{},{}\n".format(datetime.time(),self.args[0],self.dutyCycle))

            #     # update both lamps...this needs to change
            #     d_out.update({self.lamps[1] + " PWM DC": self.dutyCycle})
            #     d_out.update({self.lamps[0] + " PWM DC": self.dutyCycle})
                

            #     time.sleep(self.updatePeriod)

            # turning off lamps at the end of test
            d_out.update({self.lamps[1] + " PWM DC": 0})
            d_out.update({self.lamps[0] + " PWM DC": 0})

            Logging.logEvent("Event","End Profile", 
                {'time': datetime.time()})

            self.handeled = True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: {} in file {}:{}".format(exc_type, fname, exc_tb.tb_lineno))

            # FileCreation.pushFile("Error",self.zoneUUID,'{"errorMessage":"%s"}'%(e))
            self.running = False
            raise e
        self.running = False
        return

    def runProcess(self):
        self.checkPause()
        self.checkHold()
        self.runRamp()
        self.runSoak()

    def checkPause(self):
        if self.paused:
            inPause = True
            self.event('pause')
        else:
            inPause = False
        while self.paused:
            time.sleep(.5)
        if inPause:
            inPause = False
            self.event('endpause')
            self.timerOn = False

    def checkHold(self):
        tempHold = self.zoneProfile.thermalProfiles[self.setPoint].hold

        if self.inHold and not tempHold:
            # Hold is just turning on
            self.zoneProfile.thermalProfiles[self.setPoint].heldTemp = self.zoneProfile.thermalProfiles[self.setPoint].tempGoal
            self.zoneProfile.thermalProfiles[self.setPoint].tempGoal = self.zoneProfile.thermalProfiles[self.setPoint].temp
            self.zoneProfile.thermalProfiles[self.setPoint].hold = True
            tempHold = True
            while not self.timeStartForHold:
                self.timeStartForHold = int(time.time())
            self.event('starthold')

        if not self.inHold and tempHold:
            self.zoneProfile.thermalProfiles[self.setPoint].tempGoal = self.zoneProfile.thermalProfiles[self.setPoint].heldTemp
            self.zoneProfile.thermalProfiles[self.setPoint].heldTemp = 0
            self.zoneProfile.thermalProfiles[self.setPoint].hold = False
            if self.inSoak:
                self.releaseHold()
            self.timerOn = False
            self.event('endhold')

        if self.inHold and tempHold:
            self.tempChange = self.zoneProfile.thermalProfiles[self.setPoint].tempGoal - self.zoneProfile.thermalProfiles[
                self.setPoint].temp
            self.zoneProfile.thermalProfiles[self.setPoint].temp += self.tempChange
            time.sleep(.5)
            # This might cause a stack overflow...
            self.checkHold()

    def runRamp(self):
        if self.inRamp:
            if not self.timerOn:
                self.timer = time.time()
                self.timerOn = True

            tempDelta = self.zoneProfile.thermalProfiles[self.setPoint].tempGoal - self.zoneProfile.thermalProfiles[self.setPoint].temp
            rampDuration = self.zoneProfile.thermalProfiles[self.setPoint].ramp
            rampRunTime = time.time() - self.timer
            rampDuration = (rampDuration - rampRunTime) / 60
            changePerMin = tempDelta / rampDuration

            status = {
                "Temp Error off Goal": tempDelta,
                "Ramp Duration": rampDuration,
                "Ramp Run Time": rampRunTime,
                "Needed Change / Min": changePerMin,
                "UpdatePeriod" : self.updatePeriod,
            }
            Logging.logEvent("Debug","Data Dump", 
                {"message": "Current Ramp Status",
                 "level":4,
                 "dict":status})

            if(changePerMin > 0):
                minsToResult = tempDelta / changePerMin
            else:
                minsToResult = 0

            if(self.updatePeriod > 0):
                self.runCount = round((minsToResult * 60)/self.updatePeriod)
            else:
                self.runCount = 0
                self.inRamp = False

            if self.runCount <= 0:
                self.inRamp = False


            self.tempChange = (changePerMin * self.updatePeriod) / 60

            self.event('ramp')

    def runSoak(self):
        if not self.inRamp and not self.inSoak and not self.soakComplete:
            self.inSoak = True
            if (self.updatePeriod > 0):
                self.runCount = (self.zoneProfile.thermalProfiles[self.setPoint].soakduration) /  self.updatePeriod
            else:
                self.inSoak = False
                self.soakComplete = True

        if self.inSoak:
            self.tempChange = self.zoneProfile.thermalProfiles[self.setPoint].tempGoal - self.zoneProfile.thermalProfiles[self.setPoint].temp
            self.runCount -= 1
            self.event('soak')
            if self.runCount <= 0:
                thermalProfileCount = len(self.zoneProfile.thermalProfiles) - 1
                if self.setPoint < thermalProfileCount:
                    self.setPoint += 1
                    self.inRamp = True
                    self.inSoak = False
                    self.runCount = 1
                    # self.zoneProfile.thermalProfiles[self.setPoint].temp = self.zoneProfile.getTemp("Max")
                    print("Moving onto next setpoint")
                else:
                    self.reset()

    def releaseHold(self):
        timeEndForHold = None
        while not timeEndForHold:
            timeEndForHold = int(time.time())
        diff = timeEndForHold - self.timeStartForHold
        d = divmod(diff, 86400)  # days
        h = divmod(d[1], 3600)  # hours
        m = divmod(h[1], 60)  # minutes
        self.zoneProfile.thermalProfiles[self.setPoint].soakduration += m[1]

    def reset(self):
        print("DEBUG: HW control reset")
        self.inRamp = False
        self.inSoak = False
        self.soakComplete = True


    def terminate(self):
        self.reset()
        self.runCount = 0
        self.event("abort")

    def event(self,eventName):
        eventCreated = '{"event":"%s","profileuuid":"%s","zoneuuid":"%s","Zone":"%s","ChangeSteps":"%s", "Temp":"%s", "inRamp":"%s", "insoak":"%s" }'%\
               (eventName,self.zoneProfile.profileUUID,self.zoneProfile.zoneUUID,self.args[0] ,self.runCount,(self.zoneProfile.thermalProfiles[self.setPoint].temp),self.inRamp,self.inSoak)

        # MySQlConnect.pushEvent(eventCreated)
        # print(eventCreated)
        return eventCreated





