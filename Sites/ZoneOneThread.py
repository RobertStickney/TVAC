from DataContracts.ProfileInstance import ProfileInstance

class ZoneThread("zone1"):
    zonesInstance = ProfileInstance.getInstance()
    stepInfo = zonesInstance.zoneProfiles.getZone("zone1")
