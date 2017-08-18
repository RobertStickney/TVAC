from DataContracts.HardwareStatusInstance import HardwareStatusInstance
from DataContracts.ThermalProfileContract import ThermalProfileContract

from HouseKeeping.globalVars import debugPrint

class ZoneProfileContract:
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
        hwStatus = HardwareStatusInstance.getInstance()
        list = []
        for tc in thermocouples:
            list.append(hwStatus.Thermocouples.getTC(tc))
        return list

    def setTermalProfiles(self,termalProfiles):
        list = []
        for profile in termalProfiles:
            list.append(ThermalProfileContract(profile))
        return list

    def update(self, d):
        debugPrint(4, "Updating zone with info:\n{}".format(d))
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
            self.thermocouples = self.setThermocouples(d['thermalcouples'])

    def getJson(self):
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
        coupleLen = len(self.thermalCouples)
        count = 0
        for couple in self.thermalCouples:
            message.append(couple.getJson())
            if count < (coupleLen - 1):
                message.append(',')
                count = count + 1

        message.append(']}')
        test = ''.join(message)
        return test