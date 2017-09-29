import uuid
import time
import datetime

from ThreadControls.HardWareControlStub import HardWareControlStub
from ThreadControls.SafetyCheck import SafetyCheck
from ThreadControls.ThermoCoupleUpdater import ThermoCoupleUpdater
from ThreadControls.TsRegistersControlStub import TsRegistersControlStub
from ThreadControls.LN2Updater import LN2Updater
from ThreadControls.PfeifferGaugeControlStub import PfeifferGaugeControlStub
from ThreadControls.VacuumControlStub import VacuumControlStub
from ThreadControls.ShiMccControlStub import ShiMccControlStub


from Collections.ProfileInstance import ProfileInstance

from Logging.MySql import MySQlConnect
from Logging.Logging import Logging

class ThreadCollection:

    def __init__(self):
        self.zoneThreadDict = self.createZoneCollection()
        self.hardwareInterfaceThreadDict = self.createHardwareInterfaces(parent=self)
        self.safetyThread = SafetyCheck(parent=self)

        self.zoneProfiles = ProfileInstance.getInstance().zoneProfiles

        self.runHardwareInterfaces()

        # if there is a half finished profile in the database
        if not self.zoneProfiles.getActiveProfileStatus():
            profileName, startTime = self.returnActiveProfile()
            # If there is one
            if profileName:
                # self.zoneProfiles.activeProfile = True
                # load up ram (zone collection) with info from the database and the given start time
                self.zoneProfiles.loadProfile(profileName,startTime)
                # after it's in memory, run it!
                self.runProfile(firstStart = False)
            else:
                # If there is an error, it's stored here so return it
                if startTime:
                    return startTime
                #No error
            # End of If profile found
        # end if no active profile
    #end of function 


    def returnActiveProfile(self):
        '''
        A helper function that will look in the DB to see if there is any half finished profile instances
        Returns the profile profile_name and Profile ID if there is, False, False if not
        '''
        sql = "SELECT profile_name, startTime FROM tvac.Profile_Instance WHERE endTime IS NULL;"
        mysql = MySQlConnect()
        try:
            mysql.cur.execute(sql)
            mysql.conn.commit()
        except Exception as e:
            return False, e

        result = mysql.cur.fetchone()
        if not result:
            return False, False
        return result['profile_name'], result['startTime']
        
    def createZoneCollection(self):
        return {
            "zone1": HardWareControlStub(args=('zone1',), kwargs=({'pause': 10}),lamps=['IR Lamp 1','IR Lamp 2']),
            "zone2": HardWareControlStub(args=('zone2',),lamps=['IR Lamp 3','IR Lamp 4']),
            "zone3": HardWareControlStub(args=('zone3',),lamps=['IR Lamp 6','IR Lamp 5']),
            "zone4": HardWareControlStub(args=('zone4',),lamps=['IR Lamp 7','IR Lamp 8']),
            "zone5": HardWareControlStub(args=('zone5',),lamps=['IR Lamp 9','IR Lamp 10']),
            "zone6": HardWareControlStub(args=('zone6',),lamps=['IR Lamp 12','IR Lamp 11']),
            "zone7": HardWareControlStub(args=('zone7',),lamps=['IR Lamp 13','IR Lamp 14']),
            "zone8": HardWareControlStub(args=('zone8',),lamps=['IR Lamp 15','IR Lamp 16']),
            # zone9 is the platen
            # "zone9": HardWareControlStub(args=('zone9',))
            }

    def createHardwareInterfaces(self,parent):
        # sending parent for testing, getting current profile data to zone instance
        return {
            1: TsRegistersControlStub(parent=parent),
            2: ThermoCoupleUpdater(parent=parent),
            3: PfeifferGaugeControlStub(),
            4: ShiMccControlStub(),
            # 5: ShiCompressorControlStub)(),
            6: LN2Updater(ThreadCollection=parent),
            7: VacuumControlStub(),
            }


    def runHardwareInterfaces(self):
        # Starts all the hw threads
        try:
            for key in sorted(self.hardwareInterfaceThreadDict.keys()):
                self.hardwareInterfaceThreadDict[key].daemon = True
                self.hardwareInterfaceThreadDict[key].start()
            self.safetyThread.daemon = True
            self.safetyThread.start()
        except Exception as e:
            raise e
            # TODO: Add an error logger to this error



    def addProfileInstancetoBD(self):
        '''
        This is a helper function of runProfile that adds the new profile Instance to the DB
        '''

        coloums = "( profile_name, profile_I_ID, startTime )"
        values = "( \"{}\",\"{}\", \"{}\" )".format(self.zoneProfiles.profileName,self.zoneProfiles.profileUUID, datetime.datetime.fromtimestamp(time.time()))
        sql = "INSERT INTO tvac.Profile_Instance {} VALUES {};".format(coloums, values)
        # print(sql)
        mysql = MySQlConnect()
        try:
            mysql.cur.execute(sql)
            mysql.conn.commit()
        except Exception as e:
            return e

        return True


    def runProfile(self, firstStart=True):
        '''
        This assumes a profile is already loaded in RAM, it will start the profile
        Also making an entry in the DB
        '''

        # Check to make sure there is an active profile in memory
        if not self.zoneProfiles.profileName:
            return "{'Error':'No Profile loaded in memory'}"
    
        if firstStart:
            result = self.addProfileInstancetoBD()
            # If there is an error connecting to the DB, return it
            if result != True:
                return result

        # starts all the HWcontrol threads
        try:
            for thread in self.zoneThreadDict:
                if self.zoneThreadDict[thread].zoneProfile.zone > 0:
                    self.zoneThreadDict[thread].running = True
                    self.zoneThreadDict[thread].daemon = True
                    self.zoneThreadDict[thread].start()
                    Logging.logEvent("Debug","Status Update", 
                    {"message": "Zone {} is handled, about the start".format(self.zoneThreadDict[thread].zoneProfile.zone),
                     "level":1})
        except Exception as e:
            pass

        ProfileInstance.getInstance().activeProfile = True

        return "{'result':'success'}"
        


    # TODO: Check to see if we need this?
    # commenting this out because I don't think we need it
    # def runSingleThread(self,data):
    #     thread = data['zone']
    #     if self.zoneThreadDict[thread].handeled:
    #         self.zoneThreadDict[thread] = HardWareControlStub(args=(thread,))
    #     self.zoneThreadDict[thread].running = True
    #     self.zoneThreadDict[thread].daemon = True
    #     self.zoneThreadDict[thread].start()

    # TODO Why is this here?
    # def checkThreadStatus(self):
    #     for thread in self.zoneThreadDict:
    #         isAlive = self.zoneThreadDict[thread].is_alive()
    #         handled = self.zoneThreadDict[thread].handeled
    #         # print("{} is {} and is {} handled".format(thread, "ALIVE" if isAlive else "DEAD", "NOT" if not handled else ""))

    def pause(self,data=None):
        if data:
            thread = data['zone']
            self.zoneThreadDict[thread].paused = True;
            return
        for zone in self.zoneThreadDict:
            self.zoneThreadDict[zone].paused = True;

    def removePause(self,data=None):
        if data:
            thread = data['zone']
            self.zoneThreadDict[thread].paused = False
            return
        for zone in self.zoneThreadDict:
            self.zoneThreadDict[zone].paused = False;

    def holdThread(self,data=None):
        if data:
            thread = data['zone']
            self.zoneThreadDict[thread].inHold = True
            return
        for zone in self.zoneThreadDict:
            self.zoneThreadDict[zone].inHold = True;            

    def releaseHoldThread(self,data=None):
        if data:
            thread = data['zone']
            self.zoneThreadDict[thread].inHold = False
            return
        for zone in self.zoneThreadDict:
            self.zoneThreadDict[zone].inHold = False;


    def abortThread(self,data):
        thread = data['zone']
        self.zoneThreadDict[thread].terminate()
        self.zoneThreadDict[thread] = HardWareControlStub(args=(thread,))

    # TODO Why is this here?
    # def calculateRamp(self,data):
    #     thread = data['zone']
    #     self.zoneThreadDict[thread].calculateRamp()
