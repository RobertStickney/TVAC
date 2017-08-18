from DataContracts.ThermocoupleCollection import ThermocoupleCollection
#from DataContracts.PfeiferGuageCollection import PfeiferGuageCollection
#from DataContracts.ShiCryopumpCollection import ShiCryopumpCollection

from HouseKeeping.globalVars import debugPrint

class HardwareStatusInstance:
    # Here will be the instance stored.
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if HardwareStatusInstance.__instance == None:
            HardwareStatusInstance()
        return HardwareStatusInstance.__instance

    def __init__(self):
        if HardwareStatusInstance.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            debugPrint(2,"Creating HardwareStatusInstance")
            self.Thermocouples = ThermocoupleCollection()
            #self.PfeifferGuages = PfeiferGuageCollection()
            #self.ShiCryopump = ShiCryopumpCollection()
            HardwareStatusInstance.__instance = self
