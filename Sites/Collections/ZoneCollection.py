import uuid
import datetime
import time
import os
import math
from DataContracts.ZoneProfileContract import ZoneProfileContract
from Collections.HardwareStatusInstance import HardwareStatusInstance

from Logging.MySql import MySQlConnect
from Logging.Logging import Logging

class ZoneCollection:

    def __init__(self, parent):
        Logging.debugPrint(2,"Creating ZoneCollection")
        self.zoneDict = self.buildCollection()
        self.updatePeriod = 10
        self.profileUUID = uuid.uuid4()
        self.profileName = None
        self.parent = parent
        self.thermalStartTime = None

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


    def getActiveProfileStatus(self):
        '''
        This loops through all the zones in the profile, if they are all inactive it will return False
        if any of them are active, it returns true
        '''
        for zone in self.zoneDict:
            if self.zoneDict[zone].activeZoneProfile:
                return True
        return False
        
    def getHotestThermalCouple(self):
        hottest = 0
        for zone in self.zoneDict:
            if self.zoneDict[zone].activeZoneProfile:
                if self.zoneDict[zone].getTemp("Max") > hottest:
                    hottest = self.zoneDict[zone].getTemp("Max")
        return hottest

    def loadThermoCouples(self, profileName, zone):
        '''
        This is a helper medthod for LoadProfile, this will load thermocouples tied to this profile
        '''

        sql = "SELECT * FROM tvac.TC_Profile WHERE profile_name=\"{}\" AND zone=\"{}\";".format(profileName,zone)
        mysql = MySQlConnect()
        try:
            mysql.cur.execute(sql)
            mysql.conn.commit()
        except Exception as e:
            Logging.debugPrint(3,"sql: {}".format(sql))
            Logging.debugPrint(1, "Error in loadThermoCouples, zoneCollection: {}".format(str(e)))
            if Logging.debug:
                raise e2

        results = mysql.cur.fetchall()
        TCs = []
        tcList = HardwareStatusInstance.getInstance().Thermocouples.tcList
        for result in results:
            TCs.append(int(result['thermocouple']))

        for tc in tcList:
            if tc.Thermocouple in TCs:
                tc.update({"zone":"zone"+str(int(result['zone'])),"userDefined":True})
        return TCs

    def loadThermalProfiles(self, profileName, zone):
        '''
        This is a helper medthod for LoadProfile, this will load thermal profiles
        '''
        sql = "SELECT * FROM tvac.Thermal_Profile WHERE profile_name=\"{}\" AND zone=\"{}\";".format(profileName,zone)
        mysql = MySQlConnect()
        try:
            mysql.cur.execute(sql)
            mysql.conn.commit()
        except Exception as e:
            Logging.debugPrint(3,"sql: {}".format(sql))
            Logging.debugPrint(1, "Error in loadThermoProfiles, zoneCollection: {}".format(str(e)))
            if Logging.debug:
                raise e

        results = mysql.cur.fetchall()
        thermalprofiles = []
        for result in results:
            TP = {}
            TP['thermalsetpoint'] = int(result['set_point'])
            TP['tempgoal'] = float(result['temp_goal'])
            TP['soakduration'] = int(result['soak_time'])
            TP['ramp'] = int(result['ramp_time'])
            thermalprofiles.append(TP)
            
        return thermalprofiles

    def loadProfile(self, profileName, profileStartTime=None, thermalStartTime=None, firstSoakStartTime=None):
        '''
        This will take a profile loaded in the DB and put it in RAM
        If this is a pre exisiting profile we are loading after reboot, a startTime will be given
        this is the startTime of the profileInstance that was/will be ran by the ThreadCollection
        '''
        if thermalStartTime:
            Logging.debugPrint(2,"Loading profile {}:\tpst: {}\ttst: {}\tfsst: {}".format(profileName,
                                profileStartTime, time.mktime(thermalStartTime.timetuple()), firstSoakStartTime))
        else:
            Logging.debugPrint(2,"No thermalStartTime")
        try:
            sql = "SELECT zone, average, min_heat_error, max_heat_error, max_heat_per_min FROM tvac.Thermal_Zone_Profile WHERE profile_name=\"{}\";".format(profileName)
            mysql = MySQlConnect()
            try:
                mysql.cur.execute(sql)
                mysql.conn.commit()
            except Exception as e:
                Logging.debugPrint(3,"sql: {}".format(sql))
                Logging.debugPrint(1, "Error in loadProfile, zoneCollection: {}".format(str(e)))
                if Logging.debug:
                    raise e

            results = mysql.cur.fetchall()
            if not results:
                return "{'Error':'No profile loaded under that name.'}"

            # Collect this from the database..somehow if startTime not none
            self.profileUUID = uuid.uuid4()
            self.profileName = profileName
            self.profileStartTime = profileStartTime
            self.thermalStartTime = thermalStartTime
            self.firstSoakStartTime = firstSoakStartTime

            Logging.debugPrint(2,"Loaded profile: {}".format(profileName))

            for result in results:
                zoneProfile = {}
                zoneName = "zone"+str(result['zone'])
                # TODO: This is where I fix the bug where each zone has it's own ID and gets a new one on reload
                zoneProfile['profileuuid'] = self.profileUUID
                zoneProfile['zone'] = result['zone']
                zoneProfile['zoneuuid'] = uuid.uuid4()
                zoneProfile['average'] = result['average']
                zoneProfile['max_heat_error'] = result['max_heat_error']
                zoneProfile['min_heat_error'] = result['min_heat_error']
                zoneProfile['max_heat_per_min'] = result['max_heat_per_min']
                try:
                    zoneProfile['thermalprofiles'] = self.loadThermalProfiles(profileName,result['zone'])
                except Exception as e:
                    raise e
                
                try:
                    zoneProfile["thermocouples"] = self.loadThermoCouples(profileName, result['zone'])
                except Exception as e:
                    raise e

                # After you have all the data on the zone, add it to the instance
                Logging.debugPrint(3, "Loaded Profile Data Zone {}: ".format(zoneProfile['zone']),zoneProfile)
                self.zoneDict[zoneName].update(zoneProfile)
                self.zoneDict[zoneName].activeZoneProfile = True

            # TODO: This needs to be fixed
            self.parent.getInstance().vacuumWanted = True

            return "{'result':'success'}"
        except Exception as e:
            return {'result':'{}'.format(str(e))}
        

    def saveZone(self, name, zoneProfile):
        '''
        This is a helper functiont for saveProfile. It saves the data needed for each zone into the DB
        '''
        average = zoneProfile["average"]
        zone = zoneProfile["zone"]
        heatError = zoneProfile["maxTemp"]
        minTemp = zoneProfile["minTemp"]
        maxSlope =zoneProfile["maxSlope"]

        coloums = "( profile_name, zone, average, max_heat_error, min_heat_error, max_heat_per_min )"
        values = "( \"{}\",{},\"{}\",{},{},{} )".format(name,zone,average, heatError, minTemp, maxSlope)
        sql = "INSERT INTO tvac.Thermal_Zone_Profile {} VALUES {};".format(coloums, values)
        mysql = MySQlConnect()
        try:
            mysql.cur.execute(sql)
            mysql.conn.commit()
        except Exception as e:
            Logging.debugPrint(3,"sql: {}".format(sql))
            Logging.debugPrint(1, "Error in saveZone, zoneCollection: {}".format(str(e)))
            raise e

        coloums = "( profile_name, zone, set_point, temp_goal, ramp_time, soak_time )"
        values = ""
        for profile in zoneProfile["thermalprofiles"]:
            setpoint = profile["thermalsetpoint"]
            tempgoal = profile["tempgoal"]
            rampTime = profile["ramp"]
            soakTime = profile["soakduration"]

            values += "( \"{}\", {}, {}, {}, {}, {} ),\n".format(name, zone, setpoint, tempgoal, rampTime, soakTime)
        sql = "INSERT INTO tvac.Thermal_Profile {} VALUES {};".format(coloums, values[:-2])
        try:
            mysql.cur.execute(sql)
            mysql.conn.commit()
        except Exception as e:
            Logging.debugPrint(3,"sql: {}".format(sql))
            Logging.debugPrint(1, "Error in saveZone, zoneCollection: {}".format(str(e)))
            raise e

        # Saving the TC as well 
        coloums = "( profile_name, zone, thermocouple )"
        values = ""
        for tc in zoneProfile["thermocouples"]:
            values += "( \"{}\", {}, {} ),\n".format(name, zone, tc)
        sql = "INSERT INTO tvac.TC_Profile {} VALUES {};".format(coloums, values[:-2])
        try:
            mysql.cur.execute(sql)
            mysql.conn.commit()
        except Exception as e:
            Logging.debugPrint(3,"sql: {}".format(sql))
            Logging.debugPrint(1, "Error in saveZone, zoneCollection: {}".format(str(e)))
            raise e


        return True

    def saveProfile(self,json):
        try:
            name = json["name"]

            sql = "SELECT * FROM tvac.Thermal_Zone_Profile WHERE profile_name=\"{}\";".format(name)
            mysql = MySQlConnect()
            mysql.cur.execute(sql)
            mysql.conn.commit()

            results = mysql.cur.fetchall()
            if results:
                return "{'result':'Error, profile already exists'}"

            for zoneProfile in json['profiles']:
                result = self.saveZone(name, zoneProfile)
                if result != True:
                    return str(result)
            Logging.logEvent("Event","Profile",
                {"message": "New Profile loaded: ({})".format(name),
                "ProfileInstance": self.parent.getInstance()})
            return "{'result':'success'}"
        except Exception as e:
            Logging.debugPrint(3,"sql: {}".format(sql))
            Logging.debugPrint(1, "Error in loadProfile, zoneCollection: {}".format(str(e)))
            return str({'result':str(e)})


    def updateThermalStartTime(self, thermalStartTime):
        '''
        This is a helper function that is called either when a profile begins the
        thermal section (when it is in a vacuum) or when the the server is restarted. 
        '''
        # This loop is to hold the program here until the temperature vaules have been loaded
        if os.name == 'posix':
            userName = os.environ['LOGNAME']
        else:
            userName = "User"

        tmpStr = ""
        for zone in self.zoneDict:
            if self.zoneDict[zone].activeZoneProfile:
                if "root" in userName:
                    while True:
                        currentTemp = self.zoneDict[zone].getTemp(self.zoneDict[zone].average)
                        Logging.debugPrint(4,"Zone Col.: currentTemp: {}".format(currentTemp))
                        if not math.isnan(currentTemp) and int(currentTemp) != 0:
                            break
                        time.sleep(.5)
                else:
                    currentTemp = self.zoneDict[zone].getTemp(self.zoneDict[zone].average)

                tmpStr += "{}_Temp = {},".format(zone, currentTemp)

        tmpStr = tmpStr[:-1]
        sql = "UPDATE tvac.Profile_Instance set thermal_Start_Time=\"{}\",{} where thermal_Start_Time is null;".format(datetime.datetime.fromtimestamp(thermalStartTime),tmpStr)
        print(sql)
        mysql = MySQlConnect()
        try:
            mysql.cur.execute(sql)
            mysql.conn.commit()
        except Exception as e:
            Logging.debugPrint(1, "Error in updateDBwithEndTime, Duty Cycle control: {}".format(str(e)))
            if Logging.debug:
                raise e
        
    def getZone(self,d):
        return self.zoneDict[d]

    def getJson(self):
        '''
        This returns a json string of the currently loaded profile 
        '''
        return ('{"profileuuid":"%s","updateperiod":%s,"profile":[ %s ]}' % (self.profileUUID,self.updatePeriod,self.fillZones()))

    def fillZones(self):
        '''password
        This is a helper function for getJson()
        '''
        message = []
        zoneLen = len(self.zoneDict)
        count = 0
        for zone in self.zoneDict:
            message.append(self.zoneDict[zone].getJson())
            if count < (zoneLen - 1):
                message.append(',')
                count = count + 1
        return ''.join(message)
