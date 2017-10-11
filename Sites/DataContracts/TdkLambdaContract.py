import threading
import json


class TdkLambdaContract:

    __lock = threading.RLock()

    def __init__(self, addr, sys_location):
        self.system_location = sys_location
        self.address = addr
        self.model_name = None
        self.software_version = None
        self.serial_number = None
        self.last_test_date = None
        self.voltage_programmed = None
        self.voltage_measured = None
        self.current_programmed = None
        self.current_measured = None
        self.Over_Voltage_SP = None
        self.Under_Voltage_SP = None
        self.output_enable = None
        self.auto_restart = None
        self.sr = None
        self.fr = None

    def GetAddress(self):
        return self.address

    def update(self, d):
        self.__lock.acquire()
        if 'Model Name' in d:
            self.model_name = d['Model Name']
        if 'Software Vir' in d:
            self.software_version = d['Software Vir']
        if 'serial number' in d:
            self.serial_number = d['serial number']
        if 'last test date' in d:
            self.last_test_date = d['last test date']
        if 'voltage programmed' in d:
            self.voltage_programmed = d['voltage programmed']
        if 'voltage measured' in d:
            self.voltage_measured = d['voltage measured']
        if 'current programmed' in d:
            self.current_programmed = d['current programmed']
        if 'current measured' in d:
            self.current_measured = d['current measured']
        if 'Over Voltage SP' in d:
            self.Over_Voltage_SP = d['Over Voltage SP']
        if 'Under Voltage SP' in d:
            self.Under_Voltage_SP = d['Under Voltage SP']
        if 'output enable' in d:
            self.output_enable = d['output enable']
        if 'auto restart' in d:
            self.auto_restart = d['auto restart']
        if 'status reg' in d:
            self.sr = d['status reg']
        if 'fault reg' in d:
            self.fr = d['status reg']
        self.__lock.release()

    def get_val(self, name):
        self.__lock.acquire()
        if name == 'Model Name':
            val = self.model_name
        elif name == 'Software Vir':
            val = self.software_version
        elif name == 'serial number':
            val = self.serial_number
        elif name == 'last test date':
            val = self.last_test_date
        elif name == 'voltage programmed':
            val = self.voltage_programmed
        elif name == 'voltage measured':
            val = self.voltage_measured
        elif name == 'current programmed':
            val = self.current_programmed
        elif name == 'current measured':
            val = self.current_measured
        elif name == 'Over Voltage SP':
            val = self.Over_Voltage_SP
        elif name == 'Under Voltage SP':
            val = self.Under_Voltage_SP
        elif name == 'output enable':
            val = self.output_enable
        elif name == 'auto restart':
            val = self.auto_restart
        elif name == 'status reg':
            val = self.sr
        elif name == 'fault reg':
            val = self.fr
        else:
            val = None
        self.__lock.release()
        return val

    def getJson(self):
        self.__lock.acquire()
        message = ['{"Address":%s,' % self.address,
                   '"System Location":%s,' % self.system_location,
                   '"Model Name":%s,' % self.model_name,
                   '"Serial Number":%s,' % self.serial_number,
                   '"Software Version":%s,' % self.software_version,
                   '"Programmed Voltage":%s,' % self.voltage_programmed,
                   '"Programmed Current":%s,' % self.current_programmed,
                   '"Measured Voltage":%s,' % self.voltage_measured,
                   '"Measured Current":%s,' % self.current_measured]
        self.__lock.release()
        return ''.join(message)
