from DataContracts.ProfileInstance import ProfileInstance
from DataContracts.HardwareStatusInstance import HardwareStatusInstance
from ThreadControls.ThreadCollectionInstance import ThreadCollectionInstance


from HouseKeeping.globalVars import debugPrint

class GetControl:

    def checkTreadStatus(self):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.checkThreadStatus()
        return "{'result':'success'}"

    def getAllThermoCoupleData(self, filler):
    	debugPrint(2, "Calling: getAllThermoCoupleData")
    	hardwareStatusInstance = HardwareStatusInstance.getInstance()
    	json = hardwareStatusInstance.Thermocouples.getJson()
    	# print(json)
    	return json

    def getAllZoneData(self, data):
    	debugPrint(2, "Calling: getAllZoneData")
    	profileInstance = ProfileInstance.getInstance()
    	zones = profileInstance.zoneProfiles.zoneDict
    	json = "{"
    	for zone in zones:
    		print(zones[zone].getJson())
    	return "{'result':'success'}"