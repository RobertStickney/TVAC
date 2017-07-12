from DataContracts.ZoneProfileContract import ZoneProfileContract


class ZoneCollection:

    def __init__(self):
        zoneDictEmpty = {}

        self.zoneDict = {"zone1":ZoneProfileContract(zoneDictEmpty),
                         "zone2":ZoneProfileContract(zoneDictEmpty),
                         "zone3":ZoneProfileContract(zoneDictEmpty),
                         "zone4":ZoneProfileContract(zoneDictEmpty),
                         "zone5":ZoneProfileContract(zoneDictEmpty),
                         "zone6":ZoneProfileContract(zoneDictEmpty),
                         "zone7":ZoneProfileContract(zoneDictEmpty),
                         "zone8":ZoneProfileContract(zoneDictEmpty),
                         "zone9":ZoneProfileContract(zoneDictEmpty)}

    def update(self,d):
        for zoneProfile in d['Profiles']:
            zoneName = "zone"+str(zoneProfile['zone'])
            self.zoneDict[zoneName].update(zoneProfile)

    def getZone(self,d):
        return self.zoneDict[d]


