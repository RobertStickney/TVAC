from DataContracts.ZoneCollection import ZoneCollection

class ZonesInstance:
    # Here will be the instance stored.
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if ZonesInstance.__instance == None:
            ZonesInstance()
        return ZonesInstance.__instance

    def __init__(self):
        if ZonesInstance.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            self.zones = ZoneCollection()
            ZonesInstance.__instance = self