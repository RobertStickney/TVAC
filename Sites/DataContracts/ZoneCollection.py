import uuid

from DataBaseController.MySql import MySQlConnect
from DataContracts.ZoneProfileContract import ZoneProfileContract

from HouseKeeping.globalVars import debugPrint

class ZoneCollection:

    def __init__(self):
        debugPrint(2,"Creating ZoneCollection")
        self.zoneDict = self.buildCollection()
        self.updatePeriod = 1
        self.profileUUID = uuid.uuid4()
        debugPrint(3,"UUID: {}\nupdatePeriod: {}\n# of Zones: {}".format(self.profileUUID,self.updatePeriod, len(self.zoneDict)))

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
        debugPrint(4, "Updating zone with info:\n{}".format(d))
        self.profileUUID = uuid.uuid4()
        for zoneProfile in d['profiles']:
            zoneProfile['profileuuid'] = self.profileUUID
            zoneName = "zone"+str(zoneProfile['zone'])
            self.zoneDict[zoneName].update(zoneProfile)
        MySQlConnect.pushProfile()

    def getZone(self,d):
        return self.zoneDict[d]

    def getJson(self):
        return ('{"profileuuid":"%s","updateperiod":%s,"profile":[ %s ]}' % (self.profileUUID,self.updatePeriod,self.fillZones()))

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
