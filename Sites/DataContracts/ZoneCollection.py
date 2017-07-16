from DataContracts.ZoneProfileContract import ZoneProfileContract


class ZoneCollection:

    def __init__(self):
        self.zoneDict = self.buildCollection()

    def buildCollection(self):
        zoneDictEmpty = {}
        return {"zone1":ZoneProfileContract(zoneDictEmpty),
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

    def getJson(self):
        #message = []
        #message.append("{'profile':[ %s ]" % self.fillZones())
        return ('{"profile":[ %s ]}' % self.fillZones())
    def fillZones(self):
        message = []
        zoneLen = len(self.zoneDict)
        count = 0
        for zone in self.zoneDict:
            message.append(self.zoneDict[zone].getJson())
            if count < (zoneLen - 1):
                message.append(',')
                count = count + 1
        return ''.join(message)




