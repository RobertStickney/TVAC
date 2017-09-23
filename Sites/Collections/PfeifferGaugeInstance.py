'''
NOTE: This is still under test:

This is the interface between the hardware and the software. 
'''

from Collections.PfeifferGaugeCollection import PfeifferGaugeCollection

from Logging.Logging import Logging


class PfeifferGaugeInstance:
    # Here will be the instance stored.
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if PfeifferGaugeInstance.__instance == None:
            PfeifferGaugeInstance()
        return PfeifferGaugeInstance.__instance

    def __init__(self):
        if PfeifferGaugeInstance.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Logging.logEvent("Debug","Status Update", 
                {"message": "Creating PfeifferGaugeInstance",
                 "level":2})
            self.gauges = PfeifferGaugeCollection()
            PfeifferGaugeInstance.__instance = self
