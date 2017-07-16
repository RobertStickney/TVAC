from DataContracts.ProfileInstance import ProfileInstance
from ThreadControls.ThreadCollectionInstance import ThreadCollectionInstance


class PostContol:

    def loadProfile(self,data):
        profileInstance = ProfileInstance.getInstance()
        profileInstance.zoneProfiles.update(data)
        return "{'result':'success'}"

    def runProfile(self,data):
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

    def checkTreadStatus(self,data):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.checkThreadStatus()
        return "{'result':'success'}"