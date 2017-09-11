from Collections.ZoneCollection import ZoneCollection

from Logging.Logging import Logging


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
            Logging.logEvent("Debug","Status Update", 
                {"message": "Creating ProfileInstance",
                 "level":2})
            self.zoneProfiles = ZoneCollection()
            ProfileInstance.__instance = self