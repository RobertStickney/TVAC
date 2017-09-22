from Collections.ProfileInstance import ProfileInstance
from Collections.HardwareStatusInstance import HardwareStatusInstance
from ThreadControls.ThreadCollectionInstance import ThreadCollectionInstance

from Logging.Logging import Logging


class PostContol:

    def loadProfile(self,data):
        profileInstance = ProfileInstance.getInstance()
        return profileInstance.zoneProfiles.loadProfile(data["profile_name"])

    def saveProfile(self, data):
        profileInstance = ProfileInstance.getInstance()
        return profileInstance.zoneProfiles.saveProfile(data)

    def runSingleProfile(self, data):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.runSingleThread(data);
        return "{'result':'success'}"

    def pauseSingleThread(self, data):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.pause(data)
        return "{'result':'success'}"

    def removePauseSingleThread(self, data):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.removePause(data)
        return "{'result':'success'}"

    def holdSingleThread(self, data):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.holdThread(data)
        return "{'result':'success'}"

    def releaseHoldSingleThread(self, data):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.releaseHoldThread(data)
        return "{'result':'success'}"

    def abortSingleThread(self, data):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.abortThread(data)
        return "{'result':'success'}"

    def calculateRamp(self, data):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.calculateRamp(data)
        return "{'result':'success'}"

    ## Todo: These functions are for engeering tests only Remove from deliverable.
    def setPC104_Digital(self, data):
        pins = HardwareStatusInstance.getInstance().PC_104
        Logging.debugPrint(3,"POST: setPC104_Digital '%s'" % data)
        pins.digital_out.update(data)
        Logging.debugPrint(4,"Digital out data: '%s'" % pins.digital_out.getJson())
        return "{'result':'success'}"

    def setPC104_Analog(self, data):
        pins = HardwareStatusInstance.getInstance().PC_104
        pins.analog_out.update(data)
        return "{'result':'success'}"




