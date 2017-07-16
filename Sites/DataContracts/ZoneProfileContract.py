from DataContracts.TermalCoupleContract import TermalCoupleContract
from DataContracts.TermalProfileContract import TermalProfileContract


class ZoneProfileContract:
    def __init__(self, d):
        if 'zone' in d:
            self.zone = d['zone']
        else:
            self.zone = 0
        if 'Average' in d:
            self.zone = d['Average']
        else:
            self.average = 0
        if 'TermalProfiles' in d:
            self.termalProfiles = self.setTermalProfiles(d['TermalProfiles'])
        else:
            self.termalProfiles = ''
        if 'ThermalCouples' in d:
            self.thermalCouples = self.setThermakCouples(d['ThermalCouples'])
        else:
            self.thermalCouples = []

    def setThermakCouples(self,thermalCouples):
        list = []
        for couple in thermalCouples:
            list.append(TermalCoupleContract(couple))
        return list

    def setTermalProfiles(self,termalProfiles):
        list = []
        for profile in termalProfiles:
            list.append(TermalProfileContract(profile))
        return list

    def update(self, d):
        if 'zone' in d:
            self.zone = d['zone']
        if 'Average' in d:
            self.average = d['Average']
        if 'TermalProfiles' in d:
            self.termalProfiles = self.setTermalProfiles(d['TermalProfiles'])
        if 'ThermalCouples' in d:
            self.thermalCouples = self.setThermakCouples(d['ThermalCouples'])

    def getJson(self):
        message = []
        message.append('{"zone":%s,' % self.zone)
        message.append('"average":%s,' % self.average)
        message.append('"termalprofiles":[')
        profileLen = len(self.termalProfiles)
        count = 0
        for profile in self.termalProfiles:
            message.append(profile.getJson())
            if count < (profileLen - 1):
                message.append(',')
                count = count + 1

        message.append('],')
        message.append('"thermalcouples":[')
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