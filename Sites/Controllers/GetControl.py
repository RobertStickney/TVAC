from Collections.ProfileInstance import ProfileInstance
from Collections.HardwareStatusInstance import HardwareStatusInstance
from ThreadControls.ThreadCollectionInstance import ThreadCollectionInstance

from Logging.Logging import Logging

class GetControl:

    def checkTreadStatus(self):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.checkThreadStatus()
        return "{'result':'success'}"

    def getAllThermoCoupleData(self):
        Logging.debugPrint(2, "Calling: getAllThermoCoupleData")  #Todo Change to logEvent()
        hardwareStatusInstance = HardwareStatusInstance.getInstance()
        json = hardwareStatusInstance.Thermocouples.getJson('K')
        # print(json)
        return json

        
    def putUnderVacuum(self):
        HardwareStatusInstance.getInstance().vacuum = True
        return "{'result':'success'}"

    def getAllZoneData(self):
        # This doesn't work...
        Logging.debugPrint(2, "Calling: getAllZoneData")  #Todo Change to logEvent()
        profileInstance = ProfileInstance.getInstance()
        zones = profileInstance.zoneProfiles.zoneDict
        json = "{"
        for zone in zones:
            print(zones[zone].getJson())
        return "{'result':'success'}"

    def getLastError(self):
        # data unused
        Logging.debugPrint(2,"Calling: Get Last Error")  #Todo Change to logEvent()
        errorList = ThreadCollectionInstance.getInstance().threadCollection.safetyThread.errorList
        tempErrorList = []
        for i, error in enumerate(errorList):
            tempErrorList.append(error)
            errorList.pop(i)
        print(errorList)
        # error = errorList[0]
        # ThreadCollectionInstance.getInstance().threadCollection.safetyThread.errorList = errorList[1:]
        # print(errorList[0])

        return str(erroList)

    def getPC104_Digital(self):
        pins = HardwareStatusInstance.getInstance().PC_104
        return '{"out":%s,"in":%s}' % (pins.digital_out.getJson(),
                                       pins.digital_in.getJson())

    def getPC104_Analog(self):
        pins = HardwareStatusInstance.getInstance().PC_104
        return '{"out":%s,"in":%s}' % (pins.analog_out.getJson(),
                                       pins.analog_in.getJson())

    def getPressureGauges(self):
        self.cryoPumpPressure = self.gauges.get_pressure_cryopump()
        self.chamberPressure = self.gauges.get_pressure_chamber()
        self.roughPumpPressure = self.gauges.get_pressure_roughpump()
        resp = dict(CryoPressure = [], ChamberPressure=[], RoughingPressure=[])
        resp['CryoPressure'].append(self.cryoPumpPressure)
        resp['ChamberPressure'].append(self.chamberPressure)
        resp['RoughingPressure'].append(self.roughPumpPressure)
        buff = json.dumps(resp)    
        return buff  

    def getZoneTemps(self):
        temps=dict(ZoneSetPoint=[],ZoneTemp=[])

        for i in range(1,10):
            zonename="zone"+i
            setpoint=threadCollection.getInstance().threadCollection.zoneThreadDict[zonename]
            ztemp=ProfileInstance.getInstance().zoneProfiles.getZone(i-1).getTemp("Max")
            temps['ZoneSetPoint'].append(setpoint)
            temps['ZoneTemp'].append(ztemp)
        buff=json.dumps(temps)               

    def runProfile(self):
        threadInstance = ThreadCollectionInstance.getInstance()
        result = threadInstance.threadCollection.runProfile();
        return result