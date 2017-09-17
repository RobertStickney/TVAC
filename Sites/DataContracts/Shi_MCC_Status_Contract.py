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
        self.RegenStep = 'Cryopump is stopped after warm up cycle is completed.'
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
                '@': "No Error",
                'B': "Warm up Timeout - Did not reach room temperature within 60 minutes. Normally an indication of lack or purge flow and/or external heater.",
                'C': "Cool down Timeout - Did not cool down within 5 hours.",
                'D': "Roughing error - Repurge cycle limit exceeded. Check cryopump vessel for leakage to chamber or atmosphere.",
                'E': "Rate of rise limit exceeded - Rate of rise cycle limit was exceeded. Check cryopump vessel for leakage to chamber or atmosphere.",
                'F': "Manual Abort - Regeneration was intentionally aborted.",
                'G': "Rough valve timeout - Rough valve was open longer than 60 minutes.",
                'H': "Illegal system state - Redundant software checks prevent unexpected software operation. Contact service center."
                }[d['Regen Error']]
        if 'Regen Step' in d:
            self.RegenStep = {
                'Z': "Start Delay",
                'A': "20 second cancellation delay.",
                'B': "Cryopump Warm up - B",
                'C': "Cryopump Warm up - C",
                'D': "Cryopump Warm up - D",
                'E': "Cryopump Warm up - E",
                'H': "Extended Purge / Repurge Cycle",
                'J': "Waiting for roughing clearance",
                'L': "Rate Of Rise",
                'M': "Cool down",
                'P': "Regeneration Completed",
                'T': "Roughing",
                'W': "Restart Delay",
                'V': "Regeneration Aborted",
                'z': "Pump is ready for operation but in stand-by mode.",
                's': "Cryopump is stopped after warm up cycle is completed.",
                }[d['Regen Step']]
        if 'Roughing Valve State' in d:
            self.RoughingValveState = d['Roughing Valve State']
        if 'Roughing Interlock' in d:
            self.RoughingInterlock = d['Roughing Interlock']
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
            val = self.CryoPump
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
