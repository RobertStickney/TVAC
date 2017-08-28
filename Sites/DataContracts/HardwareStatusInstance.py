from DataContracts.ThermocoupleCollection import ThermocoupleCollection
from DataContracts.PfeifferGuageCollection import PfeifferGuageCollection
#from DataContracts.ShiCryopumpCollection import ShiCryopumpCollection
from Keysight_34980A.ThermoCoupleUpdater import ThermoCoupleUpdater

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
            self.PfeifferGuages = PfeifferGuageCollection()
            #self.ShiCryopump = ShiCryopumpCollection()

            # Change this to be a "hardward updater" not just TC
            thermoCoupleUpdater = ThermoCoupleUpdater(self)
            thermoCoupleUpdater.start()





            HardwareStatusInstance.__instance = self
