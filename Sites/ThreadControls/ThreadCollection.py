import random

from ThreadControls.HardWareControlStub import HardWareControlStub
from ThreadControls.SafetyCheck import SafetyCheck
from ThreadControls.ThermoCoupleUpdater import ThermoCoupleUpdater
from ThreadControls.TsRegistersControlStub import TsRegistersControlStub

from Logging.Logging import Logging

class ThreadCollection:

    def __init__(self):
        self.zoneThreadDict = self.createZoneCollection()
        self.hardwareInterfaceThreadDict = self.createHardwareInterfaces(self)
        self.safetyThread = SafetyCheck(parent=self)

        for thread in self.hardwareInterfaceThreadDict.values():
            thread.daemon = True
            thread.start()
        self.safetyThread.daemon = True
        self.safetyThread.start()


    def createZoneCollection(self):
        return {"zone1": HardWareControlStub(args=('zone1',), kwargs=({'pause': 10}),lamps=['IR Lamp 1','IR Lamp 2']),
            "zone2": HardWareControlStub(args=('zone2',),lamps=['IR Lamp 3','IR Lamp 4']),
            "zone3": HardWareControlStub(args=('zone3',),lamps=['IR Lamp 5','IR Lamp 6']),
            "zone4": HardWareControlStub(args=('zone4',),lamps=['IR Lamp 7','IR Lamp 8']),
            "zone5": HardWareControlStub(args=('zone5',),lamps=['IR Lamp 9','IR Lamp 10']),
            "zone6": HardWareControlStub(args=('zone6',),lamps=['IR Lamp 11','IR Lamp 12']),
            "zone7": HardWareControlStub(args=('zone7',),lamps=['IR Lamp 13','IR Lamp 14']),
            "zone8": HardWareControlStub(args=('zone8',),lamps=['IR Lamp 15','IR Lamp 16']),
            # zone9 is the platen
            # "zone9": HardWareControlStub(args=('zone9',))
            }

    def createHardwareInterfaces(self,parent):
        # sending parent for testing, getting current profile data to zone instance
        return {
        # commented out aren't fully tested
        "TsRegistersControlStub" : TsRegistersControlStub(parent=parent),
        # "PfeifferGuage" : ThermoCoupleUpdater()
        "ThermoCoupleUpdater" : ThermoCoupleUpdater(parent=parent),
        # "MCC" : PASS
        }


    def runAllThreads(self):
        for thread in self.zoneThreadDict:
            if self.zoneThreadDict[thread].zoneProfile.zone > 0:
                if self.zoneThreadDict[thread].handeled:
                    self.zoneThreadDict[thread] = HardWareControlStub(args=(thread,))
                Logging.logEvent("Debug","Status Update", 
                {"message": "Zone {} is handled, about the start".format(self.zoneThreadDict[thread].zoneProfile.zone),
                 "level":1})
                self.zoneThreadDict[thread].daemon = True
                self.zoneThreadDict[thread].start()

    def runSingleThread(self,data):
        thread = data['zone']
        if self.zoneThreadDict[thread].handeled:
            self.zoneThreadDict[thread] = HardWareControlStub(args=(thread,))
        self.zoneThreadDict[thread].daemon = True
        self.zoneThreadDict[thread].start()

    def checkThreadStatus(self):
        # Why is this here?
        for thread in self.zoneThreadDict:
            isAlive = self.zoneThreadDict[thread].is_alive()
            handled = self.zoneThreadDict[thread].handeled
            # print("{} is {} and is {} handled".format(thread, "ALIVE" if isAlive else "DEAD", "NOT" if not handled else ""))

    def pause(self,data):
        thread = data['zone']
        self.zoneThreadDict[thread].paused = True;

    def removePause(self,data):
        thread = data['zone']
        self.zoneThreadDict[thread].paused = False

    def holdThread(self,data):
        thread = data['zone']
        self.zoneThreadDict[thread].hold = True

    def releaseHoldThread(self,data):
        thread = data['zone']
        self.zoneThreadDict[thread].hold = False

    def abortThread(self,data):
        thread = data['zone']
        self.zoneThreadDict[thread].terminate()
        self.zoneThreadDict[thread] = HardWareControlStub(args=(thread,))

    def calculateRamp(self,data):
        thread = data['zone']
        self.zoneThreadDict[thread].calculateRamp()
