import uuid

from DataContracts.ZoneProfileContract import ZoneProfileContract
# from Collections.ProfileInstance import ProfileInstance

from Logging.MySql import MySQlConnect
from Logging.Logging import Logging

class ZoneCollection:

    def __init__(self):
        Logging.debugPrint(2,"Creating ZoneCollection")
        self.zoneDict = self.buildCollection()
        self.updatePeriod = 10
        self.profileUUID = uuid.uuid4()
        self.profileName = None

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

    # def updateZoneCollection(self,d):
    #     self.profileUUID = uuid.uuid4()
    #     for zoneProfile in d['profiles']:
    #         zoneProfile['profileuuid'] = self.profileUUID
    #         zoneName = "zone"+str(zoneProfile['zone'])
    #         Logging.debugPrint(3,"zone: {}".format(zoneName))
    #         self.zoneDict[zoneName].update(zoneProfile,ThreadCollectionInstance)

        # TODO: Edit this to leave a log in event on the DB
        # Logging.logEvent("Event","Thermal Profile Update",
        #     {
        #      "profileUUID"         : self.profileUUID,
        #      "name"                : d['name'],
        #      "zoneProfile"         : zoneProfile
        #     })


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
            raise e

        results = mysql.cur.fetchall()
        TCs = []
        for result in results:
            TCs.append(int(result['thermocouple']))
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

    def loadProfile(self, profileName, startTime=None):
        '''
        This will take a profile loaded in the DB and put it in RAM
        If this is a pre exisiting profile we are loading after reboot, a startTime will be given
        this is the startTime of the profileInstance that was/will be ran by the ThreadCollection
        '''

        sql = "SELECT zone, average, heat_error FROM tvac.Thermal_Zone_Profile WHERE profile_name=\"{}\";".format(profileName)
        mysql = MySQlConnect()
        try:
            mysql.cur.execute(sql)
            mysql.conn.commit()
        except Exception as e:
            return e

        results = mysql.cur.fetchall()
        if not results:
            return "{'Error':'No profile loaded under that name.'}"

        self.profileUUID = uuid.uuid4()
        self.profileName = profileName
        self.startTime = startTime

        Logging.debugPrint(2,"Loaded profile: {}".format(profileName))

        for result in results:
            zoneProfile = {}
            zoneName = "zone"+str(result['zone'])
            # TODO: This is where I fix the bug where each zone has it's own ID and gets a new one on reload
            zoneProfile['profileuuid'] = self.profileUUID
            zoneProfile['zone'] = result['zone']
            zoneProfile['zoneuuid'] = uuid.uuid4()
            zoneProfile['average'] = result['average']
            zoneProfile['heatError'] = result['heat_error']
            try:
                zoneProfile['thermalprofiles'] = self.loadThermalProfiles(profileName,result['zone'])
            except Exception as e:
                raise e
            
            try:
                zoneProfile["thermocouples"] = self.loadThermoCouples(profileName, result['zone'])
            except Exception as e:
                raise e

            # After you have all the data on the zone, add it to the instance
            self.zoneDict[zoneName].update(zoneProfile)
            self.zoneDict[zoneName].activeZoneProfile = True

            # TODO: This needs to be fixed
            # ProfileInstance.getInstance().vacuumWanted = True

        return "{'result':'success'}"
        

    def saveZone(self, name, zoneProfile):
        '''
        This is a helper functiont for saveProfile. It saves the data needed for each zone into the DB
        '''
        average = zoneProfile["average"]
        zone = zoneProfile["zone"]
        heatError = zoneProfile["maxTemp"]
        minTemp = zoneProfile["minTemp"]
        maxSlope =zoneProfile["maxSlope"]

        # coloums = "( profile_name, zone, average, max_heat_error, min_heat_error )"
        coloums = "( profile_name, zone, average, heat_error)"
        print(heatError)
        values = "( \"{}\",{},\"{}\",{} )".format(name,zone,average, heatError)
        sql = "INSERT INTO tvac.Thermal_Zone_Profile {} VALUES {};".format(coloums, values)
        # print(sql)
        mysql = MySQlConnect()
        try:
            mysql.cur.execute(sql)
            mysql.conn.commit()
        except Exception as e:
            return e

        coloums = "( profile_name, zone, set_point, temp_goal, ramp_time, soak_time )"
        values = ""
        for profile in zoneProfile["thermalprofiles"]:
            setpoint = profile["thermalsetpoint"]
            tempgoal = profile["tempgoal"]
            rampTime = profile["ramp"]
            soakTime = profile["soakduration"]

            values += "( \"{}\", {}, {}, {}, {}, {} ),\n".format(name, zone, setpoint, tempgoal, rampTime, soakTime)
        sql = "INSERT INTO tvac.Thermal_Profile {} VALUES {};".format(coloums, values[:-2])
        # print(sql)
        try:
            mysql.cur.execute(sql)
            mysql.conn.commit()
        except Exception as e:
            return e

        #Saving the TC as well 

        coloums = "( profile_name, zone, thermocouple )"
        values = ""
        for tc in zoneProfile["thermocouples"]:
            values += "( \"{}\", {}, {} ),\n".format(name, zone, tc)
        sql = "INSERT INTO tvac.TC_Profile {} VALUES {};".format(coloums, values[:-2])
        try:
            mysql.cur.execute(sql)
            mysql.conn.commit()
        except Exception as e:
            print(sql)
            return e

        return True

    def saveProfile(self,json):
        name = json["name"]
        for zoneProfile in json['profiles']:
            result = self.saveZone(name, zoneProfile)
            if result != True:
                return str(result)
            # zoneName = "zone"+str(zoneProfile['zone'])
            # self.zoneDict[zoneName].update(zoneProfile)
            # send event saying you loaded a profile

        return "{'result':'success'}"
        
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
