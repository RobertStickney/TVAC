'''
NOTE: This is still under test:

This is the interface between the hardware and the software. 
'''

from Collections.ShiCryopumpCollection import ShiCryopumpCollection

from Logging.Logging import Logging


class ShiCryopumpInstance:
    # Here will be the instance stored.
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if ShiCryopumpInstance.__instance == None:
            ShiCryopumpInstance()
        return ShiCryopumpInstance.__instance

    def __init__(self):
        if ShiCryopumpInstance.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Logging.logEvent("Debug","Status Update", 
                {"message": "Creating ShiCryopumpInstance",
                 "level": 2})
            self.cryopump = ShiCryopumpCollection()
            ShiCryopumpInstance.__instance = self
