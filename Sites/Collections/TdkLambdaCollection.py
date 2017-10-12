import threading
from datetime import datetime
import os

from DataContracts.TdkLambdaContract import TdkLambdaContract

from Logging.Logging import Logging


class TdkLambdaCollection:

    __lock = threading.RLock()

    def __init__(self):
        Logging.logEvent("Debug","Status Update",
                {"message": "Creating TDK Lambda DC Power Supplies Collection ",
                 "level": 2})
        self.TdkLambda_ps = self.buildCollection()
        self.time = datetime.now()


    def buildCollection(self):
        power_supplies = [TdkLambdaContract(1, 'Platen Left'),
                          TdkLambdaContract(2, 'Platen Right'),
                          TdkLambdaContract(3, 'Shroud Left'),
                          TdkLambdaContract(4, 'Shroud Right')]
        return power_supplies

    def get_platen_left_addr(self):
        return self.TdkLambda_ps[0].GetAddress()

    def get_platen_right_addr(self):
        return self.TdkLambda_ps[1].GetAddress()

    def get_shroud_left_addr(self):
        return self.TdkLambda_ps[2].GetAddress()

    def get_shroud_right_addr(self):
        return self.TdkLambda_ps[3].GetAddress()

    def get_val(self, addr, name):
        return self.getPS(addr).get_val(name)

    def update(self, pgList):
        self.__lock.acquire()
        self.time = datetime.now()
        self.__lock.release()
        for updatePG in pgList:
            ps = self.getPS(updatePG['addr'])
            ps.update(updatePG)

    def getPS(self, n):
        for ps in self.TdkLambda_ps:
            if ps.GetAddress() == n:
                return ps
        raise RuntimeError('TDK Lambda Address #: %s is out of range' % n)

    def getJson(self):
        message = []
        self.__lock.acquire()
        message.append('{"time":%s,' % self.time)
        self.__lock.release()
        message.append('PGs:[%s]' %','.join([ps.getJson() for ps in self.TdkLambda_ps]))
        message.append('}')
        return ''.join(message)
