from threading import Thread
import json
import uuid
import time
import datetime

from DataBaseController.FileCreation import FileCreation
from DataBaseController.MySql import MySQlConnect
from Collections.ProfileInstance import ProfileInstance
from Collections.HardwareStatusInstance import HardwareStatusInstance
from PID.PID import PID

from HouseKeeping.globalVars import debugPrint


class HardWareControlStub(Thread):

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None, lamps=None):
        debugPrint(3,"Creating HardWareControlStub")
        debugPrint(4,"args: {}".format(args))
        Thread.__init__(self, group=group, target=target, name=name)
        self.args = args
        self.kwargs = kwargs

        profileInstance = ProfileInstance.getInstance()
        self.zoneProfile = profileInstance.zoneProfiles.getZone(self.args[0])
        self.updatePeriod = profileInstance.zoneProfiles.updatePeriod
        self.handeled = False
        self.paused = False
        self.termalProfile = 0
        self.hold = False
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
    
    def getState(self):
        '''
        This will be a simple debug medthod that will print 
        the current state of the hardware Thread
        '''
        pass


    def run(self):
        # try:
        debugPrint(2,"Running HW control Thread")
        goalTemp = self.zoneProfile.termalProfiles[self.termalProfile].tempGoal
        currentTemp = self.zoneProfile.termalProfiles[self.termalProfile].temp
        self.event('StartRun')
        debugPrint(1,"Running: {} {}".format(self.args, self.kwargs if self.kwargs else ""))
        debugPrint(1,"{}: Current/Goal temp: {}/{}".format(self.args, currentTemp,goalTemp))
        debugPrint(1,"{}: Currently: {}".format(self.args, "Alive" if self.is_alive() else "Dead"))
        hardwareStatus  = HardwareStatusInstance.getInstance()
        currentTemp = self.zoneProfile.getTemp("Max")
        debugPrint(1,"======{}: currentTemp - {}".format(self.args,currentTemp))



        self.updatePeriod = 6
        self.maxTempRisePerMin = 10
        self.maxTempRisePerUpdate = (self.maxTempRisePerMin/60)*self.updatePeriod

        self.pid = PID()
        proportional_gain = .2
        integral_gain = 0
        derivative_gain = 0
        self.pid.setKp(proportional_gain)
        self.pid.setKi(integral_gain)
        self.pid.setKd(derivative_gain)


        while self.runCount > 0:
            # print("="*100)
            # print("self.runCount :" + str(self.runCount))
            currentTemp = self.zoneProfile.getTemp("Max")
            debugPrint(1,"{}: Current/Goal temp: {}/{}".format(self.args, currentTemp,goalTemp))
            self.runProcess()

            self.zoneProfile.termalProfiles[self.termalProfile].temp += self.tempChange
            self.tempGoalTemperature = self.zoneProfile.termalProfiles[self.termalProfile].temp

            self.pid.SetPoint = self.tempGoalTemperature
            self.pid.update(currentTemp)
            error_value = self.pid.error_value
            # print("PID error_value: {}c per update?".format(error_value))
            # print("maxTempRisePerUpdate: {}c".format(self.maxTempRisePerUpdate))
            self.dutyCycle = error_value/self.maxTempRisePerUpdate
            print("percent of duty cycle: "+str(error_value/self.maxTempRisePerUpdate))
            # corrections is the "power" needed to change the temp to goal,
            # This still needs to be converted duty cylces for the heaters
            

            debugPrint(4,"{}: currentTemp: {}".format(self.args, currentTemp))
            debugPrint(4,"{}: currentGoal: {}".format(self.args, self.tempGoalTemperature))
            # someHardwareDriver.updateTemp(self.zoneProfile.termalProfiles[self.termalProfile].temp + self.tempChange)
            # hardwareStatusInstance.Thermocouples

            # update both lamps...this needs to change
            hardwareStatus.PC_104.digital_out.update({self.lamps[0] + " PWM DC": self.dutyCycle,
                                                      self.lamps[1] + " PWM DC": self.dutyCycle})
            
            # print("="*100)
            time.sleep(self.updatePeriod)
            # print(self.runCount)





        self.event('EndRun')

        self.handeled = True
        # except Exception as e:
        #     FileCreation.pushFile("Error",self.zoneUUID,'{"errorMessage":"%s"}'%(e))

        return

    def runProcess(self):
        self.checkPause()
        self.checkHold()
        self.runRamp()
        self.runSoak()

    def checkPause(self):
        debugPrint(2,"{}: Checking if paused".format(self.args))
        if self.paused:
            inPause = True
            self.event('pause')
        else:
            inPause = False
        while self.paused:
            debugPrint(2,"{}: Is paused".format(self.args))
            time.sleep(.5)
        if inPause:
            inPause = False
            self.event('endpause')
            self.timerOn = False
        # if self.paused:

        #     self.event('pause')
        # while self.paused:
        #     debugPrint(2,"{}: Is paused".format(self.args))
        #     time.sleep(.5)

    def checkHold(self):
        debugPrint(2,"{}: Checking if held".format(self.args))
        tempHold = self.zoneProfile.termalProfiles[self.termalProfile].hold

        if self.hold and not tempHold:
            # Hold is just turning on
            self.zoneProfile.termalProfiles[self.termalProfile].heldTemp = self.zoneProfile.termalProfiles[self.termalProfile].tempGoal
            self.zoneProfile.termalProfiles[self.termalProfile].tempGoal = self.zoneProfile.termalProfiles[self.termalProfile].temp
            self.zoneProfile.termalProfiles[self.termalProfile].hold = True
            tempHold = True
            while not self.timeStartForHold:
                self.timeStartForHold = int(time.time())
            self.event('starthold')

        if not self.hold and tempHold:
            self.zoneProfile.termalProfiles[self.termalProfile].tempGoal = self.zoneProfile.termalProfiles[self.termalProfile].heldTemp
            self.zoneProfile.termalProfiles[self.termalProfile].heldTemp = 0
            self.zoneProfile.termalProfiles[self.termalProfile].hold = False
            if self.inSoak:
                self.releaseHold()
            self.timerOn = False
            self.event('endhold')

        if self.hold and tempHold:
            self.tempChange = self.zoneProfile.termalProfiles[self.termalProfile].tempGoal - self.zoneProfile.termalProfiles[
                self.termalProfile].temp
            self.zoneProfile.termalProfiles[self.termalProfile].temp += self.tempChange
            time.sleep(.5)
            # This might cause a stack overflow...
            self.checkHold()

    def runRamp(self):
        debugPrint(2,"{}: Checking if in ramp".format(self.args))
        if self.inRamp:
            debugPrint(3,"{}: self.timerOn - {}".format(self.args, self.timerOn))
            if not self.timerOn:
                self.timer = time.time()
                self.timerOn = True

            # print("self.tempGoal " +str(self.zoneProfile.termalProfiles[self.termalProfile].tempGoal))
            tempDelta = self.zoneProfile.termalProfiles[self.termalProfile].tempGoal - self.zoneProfile.termalProfiles[self.termalProfile].temp
            # changePerMin = self.zoneProfile.termalProfiles[self.termalProfile].ramp
            rampDuration = self.zoneProfile.termalProfiles[self.termalProfile].ramp
            # debugPrint(3,"{}: rampRunTime - {}".format(self.args, rampRunTime))
            # debugPrint(3,"{}: rampDuration - {}".format(self.args, rampDuration))
            rampRunTime = time.time() - self.timer
            rampDuration = (rampDuration - rampRunTime) / 60
            # print("rampRunTime: {}".format(rampRunTime))
            # debugPrint(3,"{}: rampDuration - {}".format(self.args, rampDuration))
            changePerMin = tempDelta / rampDuration

            # debugPrint(3,"{}: self.timerOn - {}".format(self.args, self.timerOn))
            # debugPrint(3,"{}: rampRunTime - {}".format(self.args, rampRunTime))
            # debugPrint(3,"{}: rampDuration - {}".format(self.args, rampDuration))            
            # debugPrint(3,"{}: tempDelta - {}".format(self.args, tempDelta))
            # debugPrint(3,"{}: changePerMin - {}".format(self.args, changePerMin))

            if(changePerMin > 0):
                minsToResult = tempDelta / changePerMin
            else:
                minsToResult = 0

            # debugPrint(3,"{}: minsToResult - {}".format(self.args, minsToResult))
            # debugPrint(3,"{}: updatePeriod - {}".format(self.args, self.updatePeriod))
            if(self.updatePeriod > 0):
                self.runCount = round((minsToResult * 60)/self.updatePeriod)
            else:
                self.runCount = 0
                self.inRamp = False

            if self.runCount <= 0:
                self.inRamp = False

            # debugPrint(3,"{}: runCount - {}".format(self.args, self.runCount))
            # debugPrint(3,"{}: inRamp - {}".format(self.args, self.inRamp))

            self.tempChange = (changePerMin * self.updatePeriod) / 60
            self.event('ramp')

    def runSoak(self):
        debugPrint(2,"{}: Checking if in Soak".format(self.args))
        if not self.inRamp and not self.inSoak and not self.soakComplete:
            self.inSoak = True
            if (self.updatePeriod > 0):
                self.runCount = (self.zoneProfile.termalProfiles[self.termalProfile].soakduration) /  self.updatePeriod
            else:
                self.inSoak = False
                self.soakComplete = True

        if self.inSoak:
            self.tempChange = self.zoneProfile.termalProfiles[self.termalProfile].tempGoal - self.zoneProfile.termalProfiles[self.termalProfile].temp
            self.runCount -= 1
            self.event('soak')
            if self.runCount <= 0:
                termalProfileCount = len(self.zoneProfile.termalProfiles) - 1
                if self.termalProfile < termalProfileCount:
                    self.termalProfile += 1
                    self.inRamp = True
                    self.inSoak = False
                    self.runCount = 1
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
        self.zoneProfile.termalProfiles[self.termalProfile].soakduration += m[1]

    def reset(self):
        self.inRamp = False
        self.inSoak = False
        self.soakComplete = True


    def terminate(self):
        self.reset()
        self.runCount = 0
        self.event("abort")

    def event(self,eventName):
        eventCreated = '{"event":"%s","profileuuid":"%s","zoneuuid":"%s","Zone":"%s","ChangeSteps":"%s", "Temp":"%s", "inRamp":"%s", "insoak":"%s" }'%\
               (eventName,self.zoneProfile.profileUUID,self.zoneProfile.zoneUUID,self.args[0] ,self.runCount,(self.zoneProfile.termalProfiles[self.termalProfile].temp),self.inRamp,self.inSoak)

        # MySQlConnect.pushEvent(eventCreated)
        # print(eventCreated)
        return eventCreated





