'''
NOTE: This is still under test:

This is the interface between the hardware and the software. 
'''

from DigitalInContract import DigitalInContract
from DigitalOutContract import DigitalOutContract
from AnalogInContract import AnalogInContract
from AnalogOutContract import AnalogOutContract


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
