import random

from ThreadControls.HardWareControlStub import HardWareControlStub


class ThreadCollection:

    def __init__(self):
        self.threadDict = self.createCollection()

    def createCollection(self):
        return {"zone1": HardWareControlStub(args=('zone1',), kwargs=({'pause': 10})),
         "zone2": HardWareControlStub(args=('zone2',)),
         "zone3": HardWareControlStub(args=('zone3',)),
         "zone4": HardWareControlStub(args=('zone4',)),
         "zone5": HardWareControlStub(args=('zone5',)),
         "zone6": HardWareControlStub(args=('zone6',)),
         "zone7": HardWareControlStub(args=('zone7',)),
         "zone8": HardWareControlStub(args=('zone8',)),
         "zone9": HardWareControlStub(args=('zone9',))}

    def runAllThreads(self):
        for thread in self.threadDict:
            if self.threadDict[thread].profile.zone > 0:
                if self.threadDict[thread].handeled:
                    self.threadDict[thread] = HardWareControlStub(args=(thread,))
                self.threadDict[thread].start()

    def runSingleThread(self,data):
        thread = data['zone']
        if self.threadDict[thread].handeled:
            self.threadDict[thread] = HardWareControlStub(args=(thread,))
        self.threadDict[thread].start()

    def checkThreadStatus(self):
        for thread in self.threadDict:
            print(thread, " is alive ", self.threadDict[thread].is_alive(), ' is handeled ', self.threadDict[thread].handeled )

    def pause(self,data):
        thread = data['zone']
        self.threadDict[thread].paused = True;

    def removePause(self,data):
        thread = data['zone']
        self.threadDict[thread].paused = False

    def holdThread(self,data):
        thread = data['zone']
        self.threadDict[thread].hold = True

    def releaseHoldThread(self,data):
        thread = data['zone']
        self.threadDict[thread].hold = False

    def abortThread(self,data):
        thread = data['zone']
        self.threadDict[thread].terminate()
        self.threadDict[thread] = HardWareControlStub(args=(thread,))

    def calculateRamp(self,data):
        thread = data['zone']
        self.threadDict[thread].calculateRamp()
