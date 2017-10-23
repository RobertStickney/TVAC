import threading
from datetime import datetime

from DataContracts.Shi_MCC_Status_Contract import Shi_MCC_Status_Contract
from DataContracts.Shi_MCC_Params_Contract import Shi_MCC_Params_Contract
from DataContracts.Shi_Compressor_Contract import Shi_Compressor_Contract

from Logging.Logging import Logging

class ShiCryopumpCollection:

    __lock = threading.RLock()

    def __init__(self):
        Logging.logEvent("Debug","Status Update",
                {"message": "Creating ThermocoupleCollection",
                 "level": 2})
        self.mcc_status = Shi_MCC_Status_Contract()
        self.mcc_params = Shi_MCC_Params_Contract()
        self.compressor = Shi_Compressor_Contract()
        self.time = datetime.now()

    def update(self, d):
        self.__lock.acquire()
        self.time = datetime.now()
        self.__lock.release()
        # Logging.debugPrint(3, "ShiCryopumpCollection: {}".format(d))
        if 'MCC Status' in d:
            self.mcc_status.update(d['MCC Status'])
        if 'MCC Params' in d:
            self.mcc_params.update(d['MCC Params'])
        if 'Compressor' in d:
            self.compressor.update(d['Compressor'])

    def get_mcc_status(self, name):
        return self.mcc_status.getVal(name)

    def get_mcc_params(self, name):
        return self.mcc_params.getVal(name)

    def get_compressor(self, name):
        return self.compressor.getVal(name)

    def getJson(self):
        # temp_units values: ['K', 'C', 'F']
        # whichTCs values: ['all', 'Working', 'NotWorking']
        self.__lock.acquire()
        message = ['"time":%s' % self.time]
        self.__lock.release()
        message += ['"MCC Status":%s' % self.mcc_status.getJson(),
                    '"MCC Params":%s' % self.mcc_params.getJson(),
                    '"Compressor":%s' % self.compressor.getJson(),
                    ]
        return '{' + ','.join(message) + '}'

    def get_json_plots(self):
        self.__lock.acquire()
        message = ['"time":%s,' % self.time]
        self.__lock.release()
        message += self.mcc_status.get_json_plots()
        message += self.compressor.get_json_plots()
        return '{' + ','.join(message) + '}'
