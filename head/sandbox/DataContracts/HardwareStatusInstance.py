from DataContracts.ThermocoupleCollection import ThermocoupleCollection
#from DataContracts.PfeiferGuageCollection import PfeiferGuageCollection
#from DataContracts.ShiCryopumpCollection import ShiCryopumpCollection

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
            self.Thermocouples = ThermocoupleCollection()
            #self.PfeifferGuages = PfeiferGuageCollection()
            #self.ShiCryopump = ShiCryopumpCollection()
            HardwareStatusInstance.__instance = self
