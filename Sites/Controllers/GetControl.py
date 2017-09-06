from Collections.ProfileInstance import ProfileInstance
from Collections.HardwareStatusInstance import HardwareStatusInstance
from ThreadControls.ThreadCollectionInstance import ThreadCollectionInstance

from HouseKeeping.globalVars import debugPrint

class GetControl:

    def checkTreadStatus(self, data):
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
        # This doesn't work...
        debugPrint(2, "Calling: getAllZoneData")
        profileInstance = ProfileInstance.getInstance()
        zones = profileInstance.zoneProfiles.zoneDict
        json = "{"
        for zone in zones:
            print(zones[zone].getJson())
        return "{'result':'success'}"

    def getLastError(self, data):
        # data unused
        debugPrint(2,"Calling: Get Last Error")
        errorList = ThreadCollectionInstance.getInstance().threadCollection.safetyThread.errorList
        tempErrorList = []
        for i, error in enumerate(errorList):
            tempErrorList.append(error)
            errorList.pop(i)
        print(errorList)
        # error = errorList[0]
        # ThreadCollectionInstance.getInstance().threadCollection.safetyThread.errorList = errorList[1:]
        # print(errorList[0])

        return str(errorList)

    def getPC104_Digital(self, data):
        pins = HardwareStatusInstance.getInstance().PC_104
        return '{"out":%s,"in":%s}' % (pins.digital_out.getJson(),
                                       pins.digital_in.getJson())

    def getPC104_Analog(self, data):
        pins = HardwareStatusInstance.getInstance().PC_104
        return '{"out":%s,"in":%s}' % (pins.analog_out.getJson(),
                                       pins.analog_in.getJson())
