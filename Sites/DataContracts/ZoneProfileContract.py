from DataContracts.TermalCoupleContract import TermalCoupleContract
from DataContracts.TermalProfileContract import TermalProfileContract


class ZoneProfileContract:
    def __init__(self, d):
        if 'zone' in d:
            self.zoneID = d['zone']
        else:
            self.zone = 0
        if 'Average' in d:
            self.average = d['Average']
        else:
            self.average = 0
        if 'TermalProfiles' in d:
            self.termalProfiles = self.setTermalProfiles(d['TermalProfiles'])
        else:
            self.termalProfiles = ''
        if 'ThermalCouples' in d:
            self.thermalCouples = []
            for couple in d['ThermalCouples']:
                self.thermalCouples.append(TermalCoupleContract(couple))
        else:
            self.thermalCouples = []

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
            for couple in d['ThermalCouples']:
                self.thermalCouples.append(TermalCoupleContract(couple))