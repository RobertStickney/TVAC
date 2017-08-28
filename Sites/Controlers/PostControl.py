from DataContracts.ProfileInstance import ProfileInstance
from ThreadControls.ThreadCollectionInstance import ThreadCollectionInstance

from HouseKeeping.globalVars import debugPrint

class PostContol:

    def loadProfile(self,data):
        profileInstance = ProfileInstance.getInstance()
        profileInstance.zoneProfiles.update(data)
        return "{'result':'success'}"

    def runProfile(self,data):
        debugPrint(2,"Calling: runProfile")
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.runAllThreads();
        return "{'result':'success'}"

    def runSingleProfile(self,data):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.runSingleThread(data);
        return "{'result':'success'}"

    def pauseSingleThread(self,data):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.pause(data)
        return "{'result':'success'}"

    def removePauseSingleThread(self,data):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.removePause(data)
        return "{'result':'success'}"

    # def checkTreadStatus(self,data):
    #     # Why is this a POST and not a GET?
    #     threadInstance = ThreadCollectionInstance.getInstance()
    #     threadInstance.threadCollection.checkThreadStatus()
    #     return "{'result':'success'}"

    def holdSingleThread(self,data):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.holdThread(data)
        return "{'result':'success'}"

    def releaseHoldSingleThread(self,data):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.releaseHoldThread(data)
        return "{'result':'success'}"

    def abortSingleThread(self,data):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.abortThread(data)
        return "{'result':'success'}"

    def calculateRamp(self,data):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.calculateRamp(data)
        return "{'result':'success'}"
