import threading
from datetime import datetime

from DataContracts.Shi_MCC_Status_Contract import Shi_MCC_Status_Contract
from DataContracts.Shi_MCC_Params_Contract import Shi_MCC_Params_Contract
from DataContracts.Shi_Compressor_Contract import Shi_Compressor_Contract

from Logging.Logging import Logging

class ShiCryopumpCollection:

    __lock = threading.RLock()

    def __init__(self, addr_locations):
        Logging.logEvent("Debug","Status Update",
                {"message": "Creating ThermocoupleCollection",
                 "level": 2})
        self.pfGuageList = self.buildCollection(addr_locations)
        self.time = datetime.now()

    def update(self, d):
        self.__lock.acquire()
        self.time = datetime.now()
        self.__lock.release()
        for updatePG in d['pgList']:
            tc = self.getPG(updatePG['PG'])
            tc.update(updatePG)

    def getPG(self, n):
        for pg in self.pfGuageList:
            if pg.GetAddress() == n:
                return pg
        raise RuntimeError('Thermocouple #: %s is out of range' % n)

    def buildCollection(self, addr_locations):
        guages = []
        for a_l in addr_locations:
            guages.append(PfeifferGuageContract(a_l['addr'], a_l['loc']))
        return guages

    def getJson(self, temp_units = 'K', whichTCs = 'all'):
        # temp_units values: ['K', 'C', 'F']
        # whichTCs values: ['all', 'Working', 'NotWorking']
        message = []
        self.__lock.acquire()
        message.append('{"time":%s,' % self.time)
        self.__lock.release()
        message.append('PGs:[%s]' %','.join([pg.getJson() for pg in self.pfGuageList]))
        message.append('}')
        return ''.join(message)
