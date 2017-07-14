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
        return

    def run(self):
        tempGoal = self.profile.termalProfiles[0].tempGoal
        print('running ', self.args, self.kwargs, ' Goal temp ', tempGoal, ' temp ',
              self.profile.termalProfiles[0].temp, ' is alive ', self.is_alive())
        self.profile.termalProfiles[0].temp = tempGoal
        time.sleep(self.kwargs['pause'])
        print('running ', self.args, self.kwargs, ' Goal temp ', tempGoal, ' temp ',
              self.profile.termalProfiles[0].temp, ' is alive ', self.is_alive())
        self.handeled = True
        return