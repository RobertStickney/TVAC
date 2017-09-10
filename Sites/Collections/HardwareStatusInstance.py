from Collections.ThermocoupleCollection import ThermocoupleCollection
# from Collections.PfeifferGuageCollection import PfeifferGuageCollection
# from Collections.ShiCryopumpCollection import ShiCryopumpCollection
from Collections.PC_104_Instance import PC_104_Instance

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
            # commented out Weds sep 6, due to merge breaking something
            # self.PfeifferGuages = PfeifferGuageCollection()
            
            #self.ShiCryopump = ShiCryopumpCollection()

            self.PC_104 = PC_104_Instance.getInstance()
            HardwareStatusInstance.__instance = self
