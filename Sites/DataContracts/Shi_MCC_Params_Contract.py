import threading
import json


class Shi_MCC_Params_Contract:

    __Lock = threading.RLock()

    def __init__(self):
        self.ElapsedTime = None
        self.Failed_RateOfRise_Cycles = None
        self.FailedRepurgeCycles = None
        self.FirstStageTempCTL = {'method': None, 'temp': None}
        self.LastRateOfRiseValue = None
        self.ModuleVersion = None
        self.PowerFailureRecovery = None
        self.PowerFailureRecoveryStatus = None
        self.RegenCycles = None
        self.RegenParam = {'0': None,
                           '1': None,
                           '2': None,
                           '3': None,
                           '4': None,
                           '5': None,
                           '6': None,
                           'A': None,
                           'C': None,
                           'G': None,
                           'z': None,
                           }
        self.RegenStartDelay = None
        self.RegenStepTimer = None
        self.RegenTime = None
        self.SecondStageTempCTL = None
        self.TcPressureState = None

    def update(self, d):
        self.__Lock.acquire()
        if 'Elapsed Time' in d:
            self.ElapsedTime = d['Elapsed Time']
        if 'Failed Rate Of Rise Cycles' in d:
            self.Failed_RateOfRise_Cycles = d['Failed Rate Of Rise Cycles']
        if 'Failed Repurge Cycles' in d:
            self.FailedRepurgeCycles = d['Failed Repurge Cycles']
        if 'First Stage Temp CTL' in d:
            (m, t) = divmod(d['First Stage Temp CTL'], 400)
            self.FirstStageTempCTL['method'] = m
            self.FirstStageTempCTL['temp'] = t
        if 'Last Rate Of Rise Value' in d:
            self.LastRateOfRiseValue = d['Last Rate Of Rise Value']
        if 'MCC Version' in d:
            self.ModuleVersion = d['MCC Version']
        if 'Power Failure Recovery' in d:
            self.PowerFailureRecovery = d['Power Failure Recovery']
        if 'Power Failure Recovery Status' in d:
            self.PowerFailureRecoveryStatus = {
                0: "0: No power failure recovery in progress.",
                1: "1: Cool down in progress.",
                2: "2: Regeneration in progress.",
                3: "3: Attempting to cool pump to 17K.",
                4: "4: Recovered pump to less than 17K.",
                5: "5: Pump second stage temperature (T2) not recovering well.",
                }[d['Power Failure Recovery Status']]
        if 'Regen Cycles' in d:
            self.RegenCycles = d['Regen Cycles']
        if 'Regen Param_0' in d:
            self.RegenParam['0'] = d['Regen Param_0']
        if 'Regen Param_1' in d:
            self.RegenParam['1'] = d['Regen Param_1']
        if 'Regen Param_2' in d:
            self.RegenParam['2'] = d['Regen Param_2']
        if 'Regen Param_3' in d:
            self.RegenParam['3'] = d['Regen Param_3']
        if 'Regen Param_4' in d:
            self.RegenParam['4'] = d['Regen Param_4']
        if 'Regen Param_5' in d:
            self.RegenParam['5'] = d['Regen Param_5']
        if 'Regen Param_6' in d:
            self.RegenParam['6'] = d['Regen Param_6']
        if 'Regen Param_A' in d:
            self.RegenParam['A'] = d['Regen Param_A']
        if 'Regen Param_C' in d:
            self.RegenParam['C'] = d['Regen Param_C']
        if 'Regen Param_G' in d:
            self.RegenParam['G'] = d['Regen Param_G']
        if 'Regen Param_z' in d:
            self.RegenParam['z'] = d['Regen Param_z']
        if 'Regen Start Delay' in d:
            self.RegenStartDelay = d['Regen Start Delay']
        if 'Regen Step Timer' in d:
            self.RegenStepTimer = d['Regen Step Timer']
        if 'Regen Time' in d:
            self.RegenTime = d['Regen Time']
        if 'Second Stage Temp CTL' in d:
            self.SecondStageTempCTL = d['Second Stage Temp CTL']
        if 'Tc Pressure State' in d:
            self.TcPressureState = d['Tc Pressure State'] > 0
        self.__Lock.release()

    def getVal(self, name):
        self.__Lock.acquire()
        if name == 'Elapsed Time':
            val = self.ElapsedTime
        elif name == 'Failed Rate Of Rise Cycles':
            val = self.Failed_RateOfRise_Cycles
        elif name == 'Failed Repurge Cycles':
            val = self.FailedRepurgeCycles
        elif name == 'First Stage Temp CTL':
            val = self.FirstStageTempCTL.copy()
        elif name == 'Last Rate Of Rise Value':
            val = self.LastRateOfRiseValue
        elif name == 'MCC Version':
            val = self.ModuleVersion
        elif name == 'Power Failure Recovery':
            val = self.PowerFailureRecovery
        elif name == 'Power Failure Recovery Status':
            val = self.PowerFailureRecoveryStatus
        elif name == 'Regen Cycles':
            val = self.RegenCycles
        elif name == 'Regen Param':
            val = self.RegenParam.copy()
        elif name == 'Regen Start Delay':
            val = self.RegenStartDelay
        elif name == 'Regen Step Timer':
            val = self.RegenStepTimer
        elif name == 'Regen Time':
            val = self.RegenTime
        elif name == 'Second Stage Temp CTL':
            val = self.SecondStageTempCTL
        elif name == 'Tc Pressure State':
            val = self.TcPressureState
        else:  # Unknown Value!
            val = None
        self.__Lock.release()
        return val

    def getJson(self):
        self.__Lock.acquire()
        message = ['"Elapsed Time":%s' % json.dumps(self.ElapsedTime),
                   '"Failed Rate Of Rise Cycles":%s' % json.dumps(self.Failed_RateOfRise_Cycles),
                   '"Failed Repurge Cycles":%s' % json.dumps(self.FailedRepurgeCycles),
                   '"First Stage Temp CTL":%s' % json.dumps(self.FirstStageTempCTL),
                   '"Last Rate Of Rise Value":%s' % json.dumps(self.LastRateOfRiseValue),
                   '"MCC Version":%s' % json.dumps(self.ModuleVersion),
                   '"Power Failure Recovery":%s' % json.dumps(self.PowerFailureRecovery),
                   '"Power Failure Recovery Status":%s' % json.dumps(self.PowerFailureRecoveryStatus),
                   '"Regen Cycles":%s' % json.dumps(self.RegenCycles),
                   '"Regen Parameters":%s' % json.dumps(self.RegenParam),
                   '"Regen Start Delay":%s' % json.dumps(self.RegenStartDelay),
                   '"Regen Step Timer":%s' % json.dumps(self.RegenStepTimer),
                   '"Regen Time":%s' % json.dumps(self.RegenTime),
                   '"Second Stage Temp CTL":%s' % json.dumps(self.SecondStageTempCTL),
                   '"Tc Pressure State":%s' % json.dumps(self.TcPressureState),
                   ]
        self.__Lock.release()
        return '{' + ','.join(message) + '}'
