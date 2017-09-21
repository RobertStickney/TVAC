import threading
import json


class ShiMCC_StatusContract:

    __Lock = threading.RLock()

    def __init__(self):
        self.DutyCycle = 0
        self.FirstStageTemp = 0
        self.CryoPump = {'Motor On': False, 'Ready': False}
        self.PurgeValveState = False
        self.RegenError = ''
        self.RegenStep = ''
        self.RoughingValveState = False
        self.RoughingInterlock = {'Roughing Permission': False,
                                  'Roughing Needed': False,
                                  'Cryopump is running': False}
        self.SecondStageTemp = 0
        self.Status = {'Pump On': False,
                       'Rough Open': False,
                       'Purge Open': False,
                       'Thermocouple Gauge On': False,
                       'Power Failure Occurred': False}
        self.TcPressure = 0

    def update(self, d):
        self.__Lock.acquire()
        if 'Duty Cycle' in d:
            self.DutyCycle = d['Duty Cycle']
        if 'Stage 1 Temp' in d:
            self.FirstStageTemp = d['Stage 1 Temp']
        if 'Cryo Pump Ready State' in d:
            self.CryoPump['Motor On'] = d['Cryo Pump Ready State'][0] == '1'
            self.CryoPump['Ready'   ] = d['Cryo Pump Ready State'][1] == '1'
        if 'Purge Valve State' in d:
            self.PurgeValveState = d['Purge Valve State'] == '1'
        if 'Regen Error' in d:
            self.RegenError = {
                '@': "@: No Error",
                'B': "B: Warm up Timeout - Did not reach room temperature within 60 minutes. Normally an indication of lack or purge flow and/or external heater.",
                'C': "C: Cool down Timeout - Did not cool down within 5 hours.",
                'D': "D: Roughing error - Repurge cycle limit exceeded. Check cryopump vessel for leakage to chamber or atmosphere.",
                'E': "E: Rate of rise limit exceeded - Rate of rise cycle limit was exceeded. Check cryopump vessel for leakage to chamber or atmosphere.",
                'F': "F: Manual Abort - Regeneration was intentionally aborted.",
                'G': "G: Rough valve timeout - Rough valve was open longer than 60 minutes.",
                'H': "H: Illegal system state - Redundant software checks prevent unexpected software operation. Contact service center."
                }[d['Regen Error']]
        if 'Regen Step' in d:
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
                }[d['Regen Step']]
        if 'Roughing Valve State' in d:
            self.RoughingValveState = d['Roughing Valve State'] == 1
        if 'Roughing Interlock' in d:
            self.RoughingInterlock['Roughing Permission'] = (d['Roughing Interlock'] & 0x01) > 0  # Bit 0
            self.RoughingInterlock['Roughing Needed'    ] = (d['Roughing Interlock'] & 0x02) > 0  # Bit 0
            self.RoughingInterlock['Cryopump is running'] = (d['Roughing Interlock'] & 0x04) > 0  # Bit 0
        if 'Stage 2 Temp' in d:
            self.SecondStageTemp = d['Stage 2 Temp']
        if 'Status' in d:
            self.Status['Pump On'               ] = (d['Status'] & 0x01) > 0  # Bit 0
            self.Status['Rough Open'            ] = (d['Status'] & 0x02) > 0  # Bit 1
            self.Status['Purge Open'            ] = (d['Status'] & 0x04) > 0  # Bit 2
            self.Status['Thermocouple Gauge On' ] = (d['Status'] & 0x08) > 0  # Bit 3
            self.Status['Power Failure Occurred'] = (d['Status'] & 0x20) > 0  # Bit 5
        if 'Tc Pressure' in d:
            self.TcPressure = d['Tc Pressure']
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
        elif name == 'Tc Pressure':
            val = self.TcPressure
        else:  # Unknown Value!
            val = None
        self.__Lock.release()
        return val

    def getJson(self):
        self.__Lock.acquire()
        message = ['{"Duty Cycle":%s,' % json.dumps(self.DutyCycle),
                   '"Stage 1 Temp":%s,' % json.dumps(self.FirstStageTemp),
                   '"Cryo Pump Ready State":%s,' % json.dumps(self.CryoPump),
                   '"Purge Valve State":%s,' % json.dumps(self.PurgeValveState),
                   '"Regen Error":%s,' % self.RegenError,
                   '"Regen Step":%s,' % self.RegenStep,
                   '"Roughing Valve State":%s,' % json.dumps(self.RoughingValveState),
                   '"Roughing Interlock":%s,' % json.dumps(self.RoughingInterlock),
                   '"Stage 2 Temp":%s,' % json.dumps(self.SecondStageTemp),
                   '"Status":%s,' % json.dumps(self.Status),
                   '"Tc Pressure":%s}' % json.dumps(self.TcPressure)]
        self.__Lock.release()
        return ''.join(message)
