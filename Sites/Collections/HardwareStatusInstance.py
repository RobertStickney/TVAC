import os

from Collections.ThermocoupleCollection import ThermocoupleCollection
from Collections.PfeifferGaugeCollection import PfeifferGaugeCollection
from Collections.ShiCryopumpCollection import ShiCryopumpCollection
from Collections.TdkLambdaCollection import TdkLambdaCollection
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
            self.Shi_MCC_Cmds = []  # ['cmd', arg, arg,... arg]
            self.Shi_Compressor_Cmds = []  # 'cmd'
            self.TdkLambda_PS = TdkLambdaCollection()
            self.TdkLambda_Cmds = []  # ['cmd', arg, arg,... arg]
            self.PC_104 = PC_104_Instance.getInstance()

            # System Wide Stats
            if os.name == "posix":
                userName = os.environ['LOGNAME']
            else:
                userName = "user" 
            if "root" in userName:
                self.OperationalVacuum = False
                # self.OperationalVacuum = True
                
            else:
                self.OperationalVacuum = True
            self.VacuumState = None
            # self.VacuumState = "Operational Vacuum"

            HardwareStatusInstance.__instance = self
