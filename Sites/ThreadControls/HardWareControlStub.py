from threading import Thread
import json
import uuid
import time
import datetime
import sys
import os


<<<<<<< HEAD
# from DataBaseController.FileCreation import FileCreation
# from DataBaseController.MySql import MySQlConnect
=======
>>>>>>> f5e9f80b5a75d20e9033b47a00b81f1ea86db182
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
        self.paused = False
        self.thermalProfile = 0
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
        This will be a simple debug medthod that will give 
        the current state of the hardware Thread
        '''
        pass


    def run(self):
<<<<<<< HEAD
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
=======
        try:
            Logging.logEvent("Debug","Status Update", 
            {"message": "{}: Running HW control Thread".format(self.args[0]),
             "level":2})
>>>>>>> f5e9f80b5a75d20e9033b47a00b81f1ea86db182

            goalTemp = self.zoneProfile.thermalProfiles[self.thermalProfile].tempGoal
            currentTemp = self.zoneProfile.thermalProfiles[self.thermalProfile].temp
            

            # self.event('StartRun')
            Logging.logEvent("Event","Start Profile", 
                {'time': datetime.time()})

            hardwareStatusInstance = HardwareStatusInstance.getInstance()
            currentTemp = self.zoneProfile.getTemp("Max")

            d_out = DigitalOutContract()

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


<<<<<<< HEAD
            # update both lamps...this needs to change
            hardwareStatus.PC_104.digital_out.update({self.lamps[0] + " PWM DC": self.dutyCycle,
                                                      self.lamps[1] + " PWM DC": self.dutyCycle})
            
            # print("="*100)
            time.sleep(self.updatePeriod)
            # print(self.runCount)
=======
            while self.runCount > 0:

                currentTemp = self.zoneProfile.getTemp("Max")
                
                self.runProcess()
>>>>>>> f5e9f80b5a75d20e9033b47a00b81f1ea86db182

                self.zoneProfile.thermalProfiles[self.thermalProfile].temp += self.tempChange
                self.tempGoalTemperature = self.zoneProfile.thermalProfiles[self.thermalProfile].temp
                self.pid.SetPoint = self.tempGoalTemperature
                self.pid.update(currentTemp)
                self.dutyCycle = self.pid.error_value/self.maxTempRisePerUpdate

                status = {
                    "Current Temp": currentTemp,
                    "Setpoint Goal Temp": goalTemp,
                    "Temporary Goal Temp": self.tempGoalTemperature,
                    "Assumed Max Temp Raise per Update": self.maxTempRisePerUpdate,
                    "Percent of current duty cycle":self.dutyCycle
                }
                Logging.logEvent("Debug","Data Dump", 
                        {"message": "Current profile Status (in c)",
                         "level":4,
                         "dict":status})

                # update both lamps...this needs to change
                d_out.update({self.lamps[1] + " PWM DC": self.dutyCycle})
                d_out.update({self.lamps[0] + " PWM DC": self.dutyCycle})
                

                time.sleep(self.updatePeriod)

            # self.event('EndRun')
            Logging.logEvent("Event","End Profile")

            self.handeled = True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: {} in file {}:{}".format(exc_type, fname, exc_tb.tb_lineno))

            # FileCreation.pushFile("Error",self.zoneUUID,'{"errorMessage":"%s"}'%(e))

            raise e

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
        tempHold = self.zoneProfile.thermalProfiles[self.thermalProfile].hold

        if self.hold and not tempHold:
            # Hold is just turning on
            self.zoneProfile.thermalProfiles[self.thermalProfile].heldTemp = self.zoneProfile.thermalProfiles[self.thermalProfile].tempGoal
            self.zoneProfile.thermalProfiles[self.thermalProfile].tempGoal = self.zoneProfile.thermalProfiles[self.thermalProfile].temp
            self.zoneProfile.thermalProfiles[self.thermalProfile].hold = True
            tempHold = True
            while not self.timeStartForHold:
                self.timeStartForHold = int(time.time())
            self.event('starthold')

        if not self.hold and tempHold:
            self.zoneProfile.thermalProfiles[self.thermalProfile].tempGoal = self.zoneProfile.thermalProfiles[self.thermalProfile].heldTemp
            self.zoneProfile.thermalProfiles[self.thermalProfile].heldTemp = 0
            self.zoneProfile.thermalProfiles[self.thermalProfile].hold = False
            if self.inSoak:
                self.releaseHold()
            self.timerOn = False
            self.event('endhold')

        if self.hold and tempHold:
            self.tempChange = self.zoneProfile.thermalProfiles[self.thermalProfile].tempGoal - self.zoneProfile.thermalProfiles[
                self.thermalProfile].temp
            self.zoneProfile.thermalProfiles[self.thermalProfile].temp += self.tempChange
            time.sleep(.5)
            # This might cause a stack overflow...
            self.checkHold()

    def runRamp(self):
        if self.inRamp:
            if not self.timerOn:
                self.timer = time.time()
                self.timerOn = True

            tempDelta = self.zoneProfile.thermalProfiles[self.thermalProfile].tempGoal - self.zoneProfile.thermalProfiles[self.thermalProfile].temp
            rampDuration = self.zoneProfile.thermalProfiles[self.thermalProfile].ramp
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
                self.runCount = (self.zoneProfile.thermalProfiles[self.thermalProfile].soakduration) /  self.updatePeriod
            else:
                self.inSoak = False
                self.soakComplete = True

        if self.inSoak:
            self.tempChange = self.zoneProfile.thermalProfiles[self.thermalProfile].tempGoal - self.zoneProfile.thermalProfiles[self.thermalProfile].temp
            self.runCount -= 1
            self.event('soak')
            if self.runCount <= 0:
                thermalProfileCount = len(self.zoneProfile.thermalProfiles) - 1
                if self.thermalProfile < thermalProfileCount:
                    self.thermalProfile += 1
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
        self.zoneProfile.thermalProfiles[self.thermalProfile].soakduration += m[1]

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
               (eventName,self.zoneProfile.profileUUID,self.zoneProfile.zoneUUID,self.args[0] ,self.runCount,(self.zoneProfile.thermalProfiles[self.thermalProfile].temp),self.inRamp,self.inSoak)

        # MySQlConnect.pushEvent(eventCreated)
        # print(eventCreated)
        return eventCreated





