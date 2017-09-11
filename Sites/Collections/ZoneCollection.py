import uuid

from DataContracts.ZoneProfileContract import ZoneProfileContract

from Logging.Logging import Logging

# from DataBaseController.MySql import MySQlConnect
# from HouseKeeping.globalVars import debugPrint

class ZoneCollection:

    def __init__(self):
        Logging.logEvent("Debug","Status Update", 
        {"message": "Creating ZoneCollection",
         "level":2})
        self.zoneDict = self.buildCollection()
        self.updatePeriod = 1
        self.profileUUID = uuid.uuid4()

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
        Logging.logEvent("Debug","Status Update", 
        {"message": "Updating zone with info",
         "level":2})
        self.profileUUID = uuid.uuid4()
        for zoneProfile in d['profiles']:
            Logging.logEvent("Debug","Status Update", 
            {"message": "zone {} has thermocouples: {}".format(zoneProfile['zone'],zoneProfile['thermocouples']),
             "level":3})
            Logging.logEvent("Debug","Data Dump", 
                {"message": "Zone {}: Profile Setpoints".format(str(zoneProfile['zone'])),
                 "level":3,
                 'dict': zoneProfile['thermalprofiles']})
            zoneProfile['profileuuid'] = self.profileUUID
            zoneName = "zone"+str(zoneProfile['zone'])
            self.zoneDict[zoneName].update(zoneProfile)
        Logging.logEvent("Event","Thermal Profile Update", 
        {"profiles":d['profiles']})


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
