from ZoneContract import ZoneContract

class ZoneCollection:

    def __init__(self):
        zoneDictEmpty = {}
        listOfZones = [ZoneContract(zoneDictEmpty)];
        self.zoneDict = {"zone1":ZoneContract(zoneDictEmpty),
                         "zone2":ZoneContract(zoneDictEmpty),
                         "zone3":ZoneContract(zoneDictEmpty),
                         "zone4":ZoneContract(zoneDictEmpty),
                         "zone5":ZoneContract(zoneDictEmpty),
                         "zone6":ZoneContract(zoneDictEmpty),
                         "zone7":ZoneContract(zoneDictEmpty),
                         "zone8":ZoneContract(zoneDictEmpty),
                         "zone9":ZoneContract(zoneDictEmpty)}

    def update(self,d):
        zoneName = "zone"+str(d.zone)
        self.zoneDict[zoneName].update(d)

    def getZone(self,d):
        return self.zoneDict[d]


