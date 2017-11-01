import json
import threading


from Logging.Logging import Logging

class Shi_MCC_Status_Contract:

    __Lock = threading.RLock()

    def __init__(self):
        self.DutyCycle = None
        self.FirstStageTemp = None
        self.CryoPump = {'Motor On': None, 'Ready': None}
        self.PurgeValveState = None
        self.RegenError = None
        self.RegenStep = None
        self.RoughingValveState = None
        self.RoughingInterlock = {'Roughing Permission': None,
                                  'Roughing Needed': None,
                                  'Cryopump is Running': None,
                                  }
        self.SecondStageTemp = None
        self.Status = {'Pump On': None,
                       'Rough Open': None,
                       'Purge Open': None,
                       'Thermocouple Gauge On': None,
                       'Power Failure Occurred': None,
                       }
        self.TcPressure = None

    def update(self, d):
        self.__Lock.acquire()
        if 'DutyCycle' in d:
            self.DutyCycle = d['DutyCycle']
        if 'Stage1Temp' in d:
            self.FirstStageTemp = d['Stage1Temp']
        if 'CryoPumpReadyState' in d:
            self.CryoPump['Motor On'] = d['CryoPumpReadyState'][0] == '1'
            self.CryoPump['Ready'   ] = d['CryoPumpReadyState'][1] == '1'
        if 'PurgeValveState' in d:
            self.PurgeValveState = d['PurgeValveState'] == '1'
        if 'RegenError' in d:
            self.RegenError = {
                '@': "@: No Error",
                'B': "B: Warm up Timeout - Did not reach room temperature within 60 minutes. Normally an indication of lack or purge flow and/or external heater.",
                'C': "C: Cool down Timeout - Did not cool down within 5 hours.",
                'D': "D: Roughing error - Repurge cycle limit exceeded. Check cryopump vessel for leakage to chamber or atmosphere.",
                'E': "E: Rate of rise limit exceeded - Rate of rise cycle limit was exceeded. Check cryopump vessel for leakage to chamber or atmosphere.",
                'F': "F: Manual Abort - Regeneration was intentionally aborted.",
                'G': "G: Rough valve timeout - Rough valve was open longer than 60 minutes.",
                'H': "H: Illegal system state - Redundant software checks prevent unexpected software operation. Contact service center."
                }[d['RegenError']]
        if 'RegenStep' in d:
            self.RegenStep = {
                'Z': "Z: Start Delay",
                'A': "A: 20 second cancellation delay.",
                'B': "B: Cryopump Warm up",
                'C': "C: Cryopump Warm up",
                'D': "D: Cryopump Warm up",
                'E': "E: Cryopump Warm up",
                'H': "H: Extended Purge / Repurge Cycle",
                'J': "J: Waiting for roughing clearance",
                'L': "L: Rate Of Rise",
                'M': "M: Cool down",
                'P': "P: Regeneration Completed",
                'T': "T: Roughing",
                'W': "W: Restart Delay",
                'V': "V: Regeneration Aborted",
                'z': "z: Pump is ready for operation but in stand-by mode.",
                's': "s: Cryopump is stopped after warm up cycle is completed.",
                }[d['RegenStep']]
        if 'RoughingValveState' in d:
            self.RoughingValveState = d['RoughingValveState'] == 1
        if 'RoughingInterlock' in d:
            self.RoughingInterlock['Roughing Permission'] = (d['RoughingInterlock'] & 0x01) > 0  # Bit 0
            self.RoughingInterlock['Roughing Needed'    ] = (d['RoughingInterlock'] & 0x02) > 0  # Bit 0
            self.RoughingInterlock['Cryopump is Running'] = (d['RoughingInterlock'] & 0x04) > 0  # Bit 0
        if 'Stage2Temp' in d:
            self.SecondStageTemp = d['Stage2Temp']
        if 'Status' in d:
            self.Status['Pump On'               ] = (d['Status'] & 0x01) > 0  # Bit 0
            self.Status['Rough Open'            ] = (d['Status'] & 0x02) > 0  # Bit 1
            self.Status['Purge Open'            ] = (d['Status'] & 0x04) > 0  # Bit 2
            self.Status['Thermocouple Gauge On' ] = (d['Status'] & 0x08) > 0  # Bit 3
            self.Status['Power Failure Occurred'] = (d['Status'] & 0x20) > 0  # Bit 5
        if 'TcPressure' in d:
            self.TcPressure = d['TcPressure']
        self.__Lock.release()

    def getVal(self, name):
        self.__Lock.acquire()
        if name == 'Duty Cycle':
            val = self.DutyCycle
        elif name == 'Stage 1 Temp':
            val = self.FirstStageTemp
        elif name == 'Cryo Pump Ready State':
            val = self.CryoPump.copy()
        elif name == 'Purge Valve State':
            val = self.PurgeValveState
        elif name == 'Regen Error':
            val = self.RegenError
        elif name == 'Regen Step':
            val = self.RegenStep
        elif name == 'Roughing Valve State':
            val = self.RoughingValveState
        elif name == 'Roughing Interlock':
            val = self.RoughingInterlock.copy()
        elif name == 'Stage 2 Temp':
            val = self.SecondStageTemp
        elif name == 'Status':
            val = self.Status.copy()
        elif name == 'PumpOn?':
            val = self.Status['Pump On']
        elif name == 'Tc Pressure':
            val = self.TcPressure
        else:  # Unknown Value!
            val = None
        self.__Lock.release()
        return val

    def getJson(self):
        self.__Lock.acquire()
        message = ['"Duty Cycle (0-100)":%s' % json.dumps(self.DutyCycle),
                   '"1st stage Temp (K)":%s' % json.dumps(self.FirstStageTemp),
                   '"Cryo Pump Motor":%s' % json.dumps(self.CryoPump),
                   '"Purge Valve State":%s' % json.dumps(self.PurgeValveState),
                   '"Regen Error":%s' % json.dumps(self.RegenError),
                   '"Regen Step":%s' % json.dumps(self.RegenStep),
                   '"Roughing Valve State":%s' % json.dumps(self.RoughingValveState),
                   '"Roughing Interlock":%s' % json.dumps(self.RoughingInterlock),
                   '"2nd stage Temp (K)":%s' % json.dumps(self.SecondStageTemp),
                   '"Status":%s' % json.dumps(self.Status),
                   '"Tc Pressure":%s' % json.dumps(self.TcPressure),
                   ]
        self.__Lock.release()
        return '{' + ','.join(message) + '}'

    def get_json_plots(self):
        self.__Lock.acquire()
        message = ['"Duty Cycle (0-100)":%s' % json.dumps(self.DutyCycle),
                   '"1st stage Temp (K)":%s' % json.dumps(self.FirstStageTemp),
                   '"2nd stage Temp (K)":%s' % json.dumps(self.SecondStageTemp),
                   ]
        self.__Lock.release()
        return message
