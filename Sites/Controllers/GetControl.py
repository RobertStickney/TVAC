import json

from Collections.ProfileInstance import ProfileInstance
from Collections.HardwareStatusInstance import HardwareStatusInstance
from ThreadControls.ThreadCollectionInstance import ThreadCollectionInstance

from Logging.Logging import Logging

class GetControl:

    def checkTreadStatus(self):
        try:
            threadInstance = ThreadCollectionInstance.getInstance()
            threadInstance.threadCollection.checkThreadStatus()
            return "{'result':'success'}"
        except Exception as e:
            return "{'error':'{}'}".format(e)

    def getAllThermoCoupleData(self):
        Logging.debugPrint(2, "Calling: getAllThermoCoupleData")  #Todo Change to logEvent()
        hardwareStatusInstance = HardwareStatusInstance.getInstance()
        json = hardwareStatusInstance.Thermocouples.getJson('K')
        # print(json)
        return json


    def holdAllZones(self):
        try:
            threadInstance = ThreadCollectionInstance.getInstance()
            threadInstance.threadCollection.holdThread()
            return "{'result':'success'}"
        except Exception as e:
            return "{'error':'{}'}".format(e)

    def pauseAllZones(self):
        try:
            threadInstance = ThreadCollectionInstance.getInstance()
            threadInstance.threadCollection.pause()
            return "{'result':'success'}"
        except Exception as e:
            print("lol")
            return "{'error':'{}'}".format(str(e))

        
    def resumeAllZones(self):
        try:
            threadInstance = ThreadCollectionInstance.getInstance()
            threadInstance.threadCollection.removePause()
            return "{'result':'success'}"
        except Exception as e:
            return "{'error':'{}'}".format(e)

    def unHoldAllZones(self):
        print("!")
        try:
            threadInstance = ThreadCollectionInstance.getInstance()
            threadInstance.threadCollection.releaseHoldThread()
        except Exception as e:
            return "{'error':'{}'}".format(e)
        return "{'result':'success'}"


    def putUnderVacuum(self):
        try:
            ProfileInstance.getInstance().vacuumWanted = True
            return "{'result':'success'}"
        except Exception as e:
            return "{'error':'{}'}".format(e)

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
        tempErrorList = dict(time=[],event=[],Thermocouple=[],details=[],actions=[])
        for i, error in enumerate(errorList):
            tempErrorList['time'].append(error['time'])
            tempErrorList['event'].append(error['event'])
            tempErrorList['Thermocouple'].append(error['Thermocouple'])
            tempErrorList['details'].append(error['details'])
            tempErrorList['actions'].append(error['actions'])

            errorList.pop(i)
        Logging.debugPrint(2, "Error :" + str(errorList))
        # error = errorList[0]
        # ThreadCollectionInstance.getInstance().threadCollection.safetyThread.errorList = errorList[1:]
        # print(errorList[0])
        return json.dumps(tempErrorList)

    def getLastErrorTest(self):
        # ONLY FOR labview testing / design purposes - delete later and reference to getLastError?
        # Logging.debugPrint(2,"Calling: Get Last Error")  #Todo Change to logEvent()
        # errorList = ThreadCollectionInstance.getInstance().threadCollection.safetyThread.errorList
        tempErrorList = []
        for i in range(0,7):
            error="Error something has happened to " +str(i)
            tempErrorList.append(error)
            #errorList.pop(i)
        print(tempErrorList)
        # error = errorList[0]
        # ThreadCollectionInstance.getInstance().threadCollection.safetyThread.errorList = errorList[1:]
        # print(errorList[0])
        return json.dumps(tempErrorList)


    def hardStop(self):
        print("hard stop")
        d_out = HardwareStatusInstance.getInstance().PC_104.digital_out
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

    def getCompressorTemp(self):
        resp = {'CompressorTemp': 123}
        return json.dumps(resp)

    def getEventList(self):
        tmp = ProfileInstance.getInstance().systemStatusQueue
        ProfileInstance.getInstance().systemStatusQueue = []
        return str(tmp)
    
    def getMCCData(self):
        return HardwareStatusInstance.getInstance().ShiCryopump.mcc_status.getJson()

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
        resp = {'CryoPressure': gauges.get_cryopump_pressure(),
                'ChamberPressure': gauges.get_chamber_pressure(),
                'RoughingPressure': gauges.get_roughpump_pressure()}
        return json.dumps(resp)

    def getZoneTemps(self):
        temps=dict(ZoneTemps=[])

        for i in range(1,10):
            strzone="zone"+str(i)
            try:    
                temps['ZoneTemps'].append(ProfileInstance.getInstance().zoneProfiles.getZone(strzone).getTemp())
            except:
                temps['ZoneTemps'].append(float('nan'))

            try:
                temps['ZoneTemps'].append(ThreadCollectionInstance.getInstance().threadCollection.zoneThreadDict[strzone].pid.SetPoint)
            except:
                temps['ZoneTemps'].append(float('nan'))

        buff=json.dumps(temps)
        return buff                        

    def runProfile(self):
        threadInstance = ThreadCollectionInstance.getInstance()
        result = threadInstance.threadCollection.runProfile();
        return result
