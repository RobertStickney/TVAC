import random

from ThreadControls.HardWareControlStub import HardWareControlStub
from ThreadControls.SafetyCheck import SafetyCheck
from ThreadControls.ThermoCoupleUpdater import ThermoCoupleUpdater

from HouseKeeping.globalVars import debugPrint

class ThreadCollection:

    def __init__(self):
        self.zoneThreadDict = self.createZoneCollection()
        self.hardwareInterfaceThreadDict = self.createHardwareInterfaces()
        self.safetyThread = self.createSafetyThread()

    def createZoneCollection(self):
        return {"zone1": HardWareControlStub(args=('zone1',), kwargs=({'pause': 10})),
            "zone2": HardWareControlStub(args=('zone2',)),
            "zone3": HardWareControlStub(args=('zone3',)),
            "zone4": HardWareControlStub(args=('zone4',)),
            "zone5": HardWareControlStub(args=('zone5',)),
            "zone6": HardWareControlStub(args=('zone6',)),
            "zone7": HardWareControlStub(args=('zone7',)),
            "zone8": HardWareControlStub(args=('zone8',)),
            "zone9": HardWareControlStub(args=('zone9',)),
            # commented out so checkThreadStatus works
            # "VacGuages": "Init PfeifferGuages class here"
            }

    def createHardwareInterfaces(self):
        return {
        # commented out aren't fully tested
        # "PC_104" : TsRegistersControlStub(),
        # "PfeifferGuage" : ThermoCoupleUpdater()
        "ThermoCouple" : ThermoCoupleUpdater(),
        # "MCC" : PASS
        }

    def createSafetyThread(self):
        safetyCheck = SafetyCheck()

    def runAllThreads(self):
        for thread in self.zoneThreadDict:
            if self.zoneThreadDict[thread].zoneProfile.zone > 0:
                if self.zoneThreadDict[thread].handeled:
                    self.zoneThreadDict[thread] = HardWareControlStub(args=(thread,))
                print("Zone {} is handled, about the start".format(self.zoneThreadDict[thread].zoneProfile.zone,))
                self.zoneThreadDict[thread].start()

    def runSingleThread(self,data):
        thread = data['zone']
        if self.zoneThreadDict[thread].handeled:
            self.zoneThreadDict[thread] = HardWareControlStub(args=(thread,))
        self.zoneThreadDict[thread].start()

    def checkThreadStatus(self):
        debugPrint(2,"Starting checkThreadStatus:")
        for thread in self.zoneThreadDict:
            isAlive = self.zoneThreadDict[thread].is_alive()
            handled = self.zoneThreadDict[thread].handeled
            print("{} is {} and is {} handled".format(thread, "ALIVE" if isAlive else "DEAD", "NOT" if not handled else ""))

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
