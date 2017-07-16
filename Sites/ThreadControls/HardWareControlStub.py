from threading import Thread
import time;
import json;

from DataContracts.ProfileInstance import ProfileInstance


class HardWareControlStub(Thread):

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        Thread.__init__(self, group=group, target=target, name=name)
        self.args = args
        profileInstance = ProfileInstance.getInstance()
        self.profile = profileInstance.zoneProfiles.getZone(self.args[0])
        self.kwargs = kwargs
        self.handeled = False
        self.paused = False
        self.step = 0
        self.hold = False
        self.runCount = 0

        return

    def run(self):
        tempGoal = self.profile.termalProfiles[self.step].tempGoal
        print('running ', self.args, self.kwargs, ' Goal temp ', tempGoal, ' temp ',
              self.profile.termalProfiles[self.step].temp, ' is alive ', self.is_alive())
        self.runCount = self.kwargs['pause']

        while self.runCount > 0:
            self.profile.termalProfiles[self.step].temp = tempGoal
            self.checkPause()
            self.checkHold()
            time.sleep(1)
            self.runCount = self.runCount - 1
            print(self.runCount)

        print('running ', self.args, self.kwargs, ' Goal temp ', tempGoal, ' temp ',
              self.profile.termalProfiles[self.step].temp, ' is alive ', self.is_alive())

        self.handeled = True
        return

    def checkPause(self):
        while(self.paused):
            print('paused')
            time.sleep(.5)

    def checkHold(self):
        tempHold = self.profile.termalProfiles[self.step].hold

        if self.hold and not tempHold:
            self.profile.termalProfiles[self.step].heldTemp = self.profile.termalProfiles[self.step].tempGoal
            self.profile.termalProfiles[self.step].tempGoal = self.profile.termalProfiles[self.step].temp
            self.profile.termalProfiles[self.step].hold = True

        if not self.hold and tempHold:
            self.profile.termalProfiles[self.step].tempGoal = self.profile.termalProfiles[self.step].heldTemp
            self.profile.termalProfiles[self.step].heldTemp = 0
            self.profile.termalProfiles[self.step].hold = False

    def terminate(self):
        self.runCount = 0






