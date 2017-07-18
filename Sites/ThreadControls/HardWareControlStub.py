from threading import Thread
import time;
import json;
import uuid;

from DataContracts.ProfileInstance import ProfileInstance


class HardWareControlStub(Thread):

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        Thread.__init__(self, group=group, target=target, name=name)
        self.args = args
        self.kwargs = kwargs

        profileInstance = ProfileInstance.getInstance()
        self.profile = profileInstance.zoneProfiles.getZone(self.args[0])
        self.updatePeriod = profileInstance.zoneProfiles.updatePeriod
        self.handeled = False
        self.paused = False
        self.termalProfile = 0
        self.hold = False
        self.inRamp = True
        self.inSoak = False
        self.soakComplete = False
        self.runCount = 0
        self.tempRampStepCount = 0
        self.tempChange = 0.0
        self.UUID = uuid.uuid4()
        self.profile.update(json.loads('{"uuid":"%s"}'%self.UUID))

    def run(self):
        tempGoal = self.profile.termalProfiles[self.termalProfile].tempGoal
        print('running ', self.args, self.kwargs, ' Goal temp ', tempGoal, ' temp ',
              self.profile.termalProfiles[self.termalProfile].temp, ' is alive ', self.is_alive())
        self.runCount = self.kwargs['pause']

        while self.runCount > 0:
            self.runProcess()
            self.profile.termalProfiles[self.termalProfile].temp += self.tempChange
            time.sleep(self.updatePeriod)
            print(self.runCount)

        print('running ', self.args, self.kwargs, ' Goal temp ', tempGoal, ' temp ',
              self.profile.termalProfiles[self.termalProfile].temp, ' is alive ', self.is_alive())

        self.handeled = True
        return

    def runProcess(self):
        self.checkPause()
        self.checkHold()
        print(self.runRamp())
        print(self.runSoak())

    def checkPause(self):
        while(self.paused):
            print('paused')
            time.sleep(.5)

    def checkHold(self):
        tempHold = self.profile.termalProfiles[self.termalProfile].hold

        if self.hold and not tempHold:
            self.profile.termalProfiles[self.termalProfile].heldTemp = self.profile.termalProfiles[self.termalProfile].tempGoal
            self.profile.termalProfiles[self.termalProfile].tempGoal = self.profile.termalProfiles[self.termalProfile].temp
            self.profile.termalProfiles[self.termalProfile].hold = True

        if not self.hold and tempHold:
            self.profile.termalProfiles[self.termalProfile].tempGoal = self.profile.termalProfiles[self.termalProfile].heldTemp
            self.profile.termalProfiles[self.termalProfile].heldTemp = 0
            self.profile.termalProfiles[self.termalProfile].hold = False

    def runRamp(self):
        if self.inRamp:
            tempDelta = self.profile.termalProfiles[self.termalProfile].tempGoal - self.profile.termalProfiles[self.termalProfile].temp
            changePerMin = self.profile.termalProfiles[self.termalProfile].ramp

            if(changePerMin > 0):
                minsToResult = tempDelta / self.profile.termalProfiles[self.termalProfile].ramp
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
            return '{"ChangeSteps":"%s", "TempChange":"%s"}'%(self.runCount,(self.profile.termalProfiles[self.termalProfile].temp+self.tempChange))

    def runSoak(self):
        if not self.inRamp and not self.inSoak and not self.soakComplete:
            self.inSoak = True
            if (self.updatePeriod > 0):
                self.runCount = (self.profile.termalProfiles[self.termalProfile].soakduration * 60) /  self.updatePeriod
            else:
                self.inSoak = False
                self.soakComplete = True

        if self.inSoak:
            self.tempChange = self.profile.termalProfiles[self.termalProfile].tempGoal - self.profile.termalProfiles[self.termalProfile].temp
            self.runCount -= 1
            if self.runCount <= 0:
                termalProfileCount = len(self.profile.termalProfiles) - 1
                if self.termalProfile < termalProfileCount:
                    self.termalProfile += 1
                    self.inRamp = True
                    self.inSoak = False
                    self.runCount = 1
                else:
                    self.reset()

        return '{"Zone":"%s","ChangeSteps":"%s", "Temp":"%s", "inRamp":"%s", "insoak":"%s" }'%\
               (self.args ,self.runCount,(self.profile.termalProfiles[self.termalProfile].temp),self.inRamp,self.inSoak)

    def reset(self):
        self.inRamp = False
        self.inSoak = False
        self.soakComplete = True

    def terminate(self):
        self.runCount = 0






