from Collections.ThermocoupleCollection import ThermocoupleCollection
from Collections.PfeifferGaugeCollection import PfeifferGaugeCollection
from Collections.ShiCryopumpCollection import ShiCryopumpCollection
from Collections.PC_104_Instance import PC_104_Instance

from Logging.Logging import Logging


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
            Logging.logEvent("Debug","Status Update", 
                {"message": "Creating HardwareStatusInstance",
                 "level":2})
            self.Thermocouples = ThermocoupleCollection()
            self.PfeifferGuages = PfeifferGaugeCollection()
            self.ShiCryopump = ShiCryopumpCollection()
            self.PC_104 = PC_104_Instance.getInstance()

            # System Wide Stats
            self.OperationalVacuum = False

            HardwareStatusInstance.__instance = self
