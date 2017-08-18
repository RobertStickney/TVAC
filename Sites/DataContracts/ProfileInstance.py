from DataContracts.ZoneCollection import ZoneCollection

from HouseKeeping.globalVars import debugPrint

class ProfileInstance:
    # Here will be the instance stored.
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if ProfileInstance.__instance == None:
            ProfileInstance()
        return ProfileInstance.__instance

    def __init__(self):
        if ProfileInstance.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            debugPrint(2,"Creating ProfileInstance")
            self.zoneProfiles = ZoneCollection()
            ProfileInstance.__instance = self