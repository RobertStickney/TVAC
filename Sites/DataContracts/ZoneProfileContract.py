import threading

from Collections.HardwareStatusInstance import HardwareStatusInstance
from DataContracts.ThermalProfileContract import ThermalProfileContract

from Logging.Logging import Logging


class ZoneProfileContract:
    '''
    This is a Class that holds all the data on a given zone, this data includes:
    
    - A list of thermocouples
    - A list of thermalProfiles, this is a list of time points, ramps, soak times, and temps. 
    - The Average temp of all the TC's
    - Zone data number and UUID
    '''

    __lock = threading.RLock()

    def __init__(self, d):
        if 'zone' in d:
            self.zone = d['zone']
        else:
            self.zone = 0
        if 'profileuuid' in d:
            self.profileUUID = d['profileuuid']
        else:
            self.profileUUID = ''
        if 'average' in d:
            self.zone = d['average']
        else:
            self.average = 0
        if 'thermalprofiles' in d:
            self.thermalProfiles = self.setThermalProfiles(d['thermalprofiles'])
        else:
            self.thermalProfiles = ''
        if 'thermocouples' in d:
            self.thermocouples = self.setThermocouples(d['thermocouples'])
        else:
            self.thermocouples = []

        self.zoneUUID = ''

    def setThermocouples(self, thermocouples):
        self.__lock.acquire()
        hwStatus = HardwareStatusInstance.getInstance()
        list = []
        for tc in thermocouples:
            list.append(hwStatus.Thermocouples.getTC(tc))
        self.__lock.release()
        return list

    def setThermalProfiles(self,thermalProfiles):
        self.__lock.acquire()
        list = []
        for profile in thermalProfiles:
            list.append(ThermalProfileContract(profile))
        self.__lock.release()
        return list

    def update(self, d):
        self.__lock.acquire()
        Logging.logEvent("Debug","Data Dump",
            {"message": "Updating a zone profile",
             "level":4,
              "dict":d})
        if 'zone' in d:
            self.zone = d['zone']
        if 'profileuuid' in d:
            self.profileUUID = d['profileuuid']
        if 'zoneuuid' in d:
            self.zoneUUID = d['zoneuuid']
        if 'average' in d:
            self.average = d['average']
        if 'thermalprofiles' in d:
            self.thermalProfiles = self.setThermalProfiles(d['thermalprofiles'])
        if 'thermocouples' in d:
            self.thermocouples = self.setThermocouples(d['thermocouples'])
        self.__lock.release()


    def getTemp(self, mode=None):
        self.__lock.acquire()
        if not mode:
            mode = self.average
        if mode == "Average":
            temp = (sum(a) / len(a))
        if mode == "Min":
            temp = min(self.thermocouples, key=lambda x: x.getTemp()).getTemp()
        if mode == "Max":
            temp = max(self.thermocouples, key=lambda x: x.getTemp()).getTemp()
        self.__lock.release()
        return temp


        

    def getJson(self):
        self.__lock.acquire()
        message = ['{"zone":%s,' % self.zone,
                   '"profileuuid":"%s",' % self.profileUUID,
                   '"average":%s,' % self.average,
                   '"zoneUUID":"%s",' % self.zoneUUID,
                   '"thermalprofiles":[']
        profileLen = len(self.thermalProfiles)
        count = 0
        for profile in self.thermalProfiles:
            message.append(profile.getJson())
            if count < (profileLen - 1):
                message.append(',')
                count = count + 1

        message.append('],')
        message.append('"thermocouples":[')
        coupleLen = len(self.thermocouples)
        count = 0
        for couple in self.thermocouples:
            message.append(couple.getJson())
            if count < (coupleLen - 1):
                message.append(',')
                count = count + 1

        message.append(']}')
        self.__lock.release()
        return ''.join(message)