import threading
import json


class ShiMCC_ParamsContract:

    __Lock = threading.RLock()

    def __init__(self):
        self.ElapsedTime = 0
        self.Failed_RateOfRise_Cycles = 0
        self.FailedRepurgeCycles = 0
        self.FirstStageTempCTL = {'method': 0, 'temp': 0}
        self.LastRateOfRiseValue = 0
        self.ModuleVersion = ''
        self.PowerFailureRecovery = 0
        self.PowerFailureRecoveryStatus = 'No power failure recovery in progress.'
        self.RegenCycles = 0
        self.RegenParam = {'0': 0,
                           '1': 0,
                           '2': 0,
                           '3': 0,
                           '4': 0,
                           '5': 0,
                           '6': 0,
                           'A': 0,
                           'C': 0,
                           'G': 0,
                           'z': 0}
        self.RegenStartDelay = 0
        self.RegenStepTimer = 0
        self.RegenTime = 0
        self.SecondStageTempCTL = 0
        self.TcPressureState = False

    def update(self, d):
        self.__Lock.acquire()
        if '' in d:
            self. = d['']
        if 'First Stage Temp CTL' in d:
            (m,t) = divmod(d['First Stage Temp CTL'], 400)
            self.FirstStageTempCTL['method'] = m
            self.FirstStageTempCTL['temp'] = t
        if '' in d:
            self. = d['']
        self.__Lock.release()

    def getVal(self, name):
        self.__Lock.acquire()
        if name == 'LN2-P EN':
            val = self.DutyCycle
        elif name == '':
            val = self.
        elif name == '':
            val = self.
        elif name == '':
            val = self.
        elif name == '':
            val = self.
        elif name == '':
            val = self.
        elif name == '':
            val = self.
        elif name == '':
            val = self.
        elif name == '':
            val = self.
        elif name == '':
            val = self.
        elif name == '':
            val = self.
        elif name == '':
            val = self.
        elif name == '':
            val = self.
        elif name == '':
            val = self.
        elif name == '':
            val = self.
        elif name == '':
            val = self.
        elif name == '':
            val = self.
        elif name == '':
            val = self.
        elif name == '':
            val = self.
        elif name == '':
            val = self.
        elif name == '':
            val = self.
        else:  # Unknown Value!
            val = None
        self.__Lock.release()
        return val

    def getJson(self):
        self.__Lock.acquire()
        message = ['{"Duty Cycle":%s,' % self.DutyCycle,
                   '"Temp Stage1":%s,' % self.FirstStageTemp,
                   '"Cryo Pump Ready State":%s,' % self.CryoPumpRdyState,
                   '"Purge Valve State":%s,' % self.PurgeValveState,
                   '"Regen Error":%s,' % self.RegenError,
                   '"Regen Step":%s,' % self.RegenStep,
                   '"Roughing Valve State":%s,' % self.RoughingValveState,
                   '"Roughing Interlock":%s,' % self.RoughingInterlock,
                   '"Temp Stage2":%s,' % self.SecondStageTemp,
                   '"Status":%s,' % self.Status,
                   '"Tc Pressure":%s}' % self.TcPressure]
        self.__Lock.release()
        return ''.join(message)
