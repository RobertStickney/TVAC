import threading

# from Collections.HardwareStatusInstance import HardwareStatusInstance
# from DataContracts.ThermalProfileContract import ThermalProfileContract
#
# from HouseKeeping.globalVars import debugPrint
from HardwareStatusInstance import HardwareStatusInstance
from ThermalProfileContract import ThermalProfileContract

from globalVars import debugPrint

class ZoneProfileContract:
    '''
    This is a Class that holds all the data on a given zone, this data includes:
    
    - A list of thermocouples
    - A list of termalProfiles, this is a list of time points, ramps, soak times, and temps. 
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
        if 'termalprofiles' in d:
            self.termalProfiles = self.setTermalProfiles(d['termalprofiles'])
        else:
            self.termalProfiles = ''
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

    def setTermalProfiles(self,termalProfiles):
        self.__lock.acquire()
        list = []
        for profile in termalProfiles:
            debugPrint(4,"T-SP: {}".format(profile['termalsetpoint']))
            debugPrint(4,profile)
            list.append(ThermalProfileContract(profile))
        self.__lock.release()
        return list

    def update(self, d):
        self.__lock.acquire()
        debugPrint(4, "Updating zone profile with info:\n{}".format(d))
        if 'zone' in d:
            self.zone = d['zone']
        if 'profileuuid' in d:
            self.profileUUID = d['profileuuid']
        if 'zoneuuid' in d:
            self.zoneUUID = d['zoneuuid']
        if 'average' in d:
            self.average = d['average']
        if 'termalprofiles' in d:
            self.termalProfiles = self.setTermalProfiles(d['termalprofiles'])
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
        message = []
        message.append('{"zone":%s,' % self.zone)
        message.append('"profileuuid":"%s",' % self.profileUUID)
        message.append('"average":%s,' % self.average)
        message.append('"zoneUUID":"%s",' % self.zoneUUID)
        message.append('"termalprofiles":[')
        profileLen = len(self.termalProfiles)
        count = 0
        for profile in self.termalProfiles:
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
        test = ''.join(message)
        self.__lock.release()
        return test