from DataContracts.DigitalInContract import DigitalInContract
from DataContracts.DigitalOutContract import DigitalOutContract
from DataContracts.AnalogInContract import AnalogInContract
from DataContracts.AnalogOutContract import AnalogOutContract


class PC_104_Instance:
    # Here will be the instance stored.
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if PC_104_Instance.__instance == None:
            PC_104_Instance()
        return PC_104_Instance.__instance

    def __init__(self):
        if PC_104_Instance.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            self.digital_in = DigitalInContract()
            self.digital_out = DigitalOutContract()
            self.analog_in = AnalogInContract()
            self.analog_out = AnalogOutContract()
            PC_104_Instance.__instance = self
