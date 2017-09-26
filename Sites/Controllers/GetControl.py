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
        '''
        TODO: Right now this doesn't work, should it work?
        '''

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
        return str(errorList)


    def hardStop(self):
        print("hard stop")
        d_out = HardwareStatusInstance.getInstance().PC_104.digital_out
        zones = ThreadCollectionInstance.getInstance().threadCollection.zoneThreadDict
        ProfileInstance.getInstance().activeProfile = False
        d_out.update({"IR Lamp 1 PWM DC": 0})
        d_out.update({"IR Lamp 2 PWM DC": 0})
        d_out.update({"IR Lamp 3 PWM DC": 0})
        d_out.update({"IR Lamp 4 PWM DC": 0})
        d_out.update({"IR Lamp 5 PWM DC": 0})
        d_out.update({"IR Lamp 6 PWM DC": 0})
        d_out.update({"IR Lamp 7 PWM DC": 0})
        d_out.update({"IR Lamp 8 PWM DC": 0})
        d_out.update({"IR Lamp 9 PWM DC": 0})
        d_out.update({"IR Lamp 10 PWM DC": 0})
        d_out.update({"IR Lamp 11 PWM DC": 0})
        d_out.update({"IR Lamp 12 PWM DC": 0})
        d_out.update({"IR Lamp 13 PWM DC": 0})
        d_out.update({"IR Lamp 14 PWM DC": 0})
        d_out.update({"IR Lamp 15 PWM DC": 0})
        d_out.update({"IR Lamp 16 PWM DC": 0})
        return "{'result':'success'}"

    def getEventList(self):
        tmp = ProfileInstance.getInstance().systemStatusQueue
        ProfileInstance.getInstance().systemStatusQueue = []
        return str(tmp)
    

    def getPC104_Digital(self):
        pins = HardwareStatusInstance.getInstance().PC_104
        return '{"out":%s,"in":%s}' % (pins.digital_out.getJson(),
                                       pins.digital_in.getJson())

    def getPC104_Analog(self):
        pins = HardwareStatusInstance.getInstance().PC_104
        return '{"out":%s,"in":%s}' % (pins.analog_out.getJson(),
                                       pins.analog_in.getJson())

    def getPressureGauges(self):
        gauges = HardwareStatusInstance.getInstance().PfeifferGuages
        cryoPumpPressure = gauges.get_pressure_cryopump()
        chamberPressure = gauges.get_pressure_chamber()
        roughPumpPressure = gauges.get_pressure_roughpump()
        resp = dict("Pressure": [])
        resp['Pressure'].append(cryoPumpPressure)
        resp['Pressure'].append(chamberPressure)
        resp['Pressure'].append(roughPumpPressure)
        buff = json.dumps(resp)    
        return buff            

    def runProfile(self):
        threadInstance = ThreadCollectionInstance.getInstance()
        result = threadInstance.threadCollection.runProfile();
        return result