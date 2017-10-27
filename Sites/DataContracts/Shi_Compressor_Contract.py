import json
import threading


class Shi_Compressor_Contract:

    __Lock = threading.RLock()

    def __init__(self):
        self.return_pressure = None
        self.helium_temp = None
        self.water_in_temp = None
        self.water_out_temp = None
        self.firmware_version = None
        self.op_hours = None
        self.rs232_config = None
        self.op_state = None
        self.status = {'Solenoid ON': None,
                       'Pressure Alarm': None,
                       'Oil Level Alarm': None,
                       'Water Flow Alarm': None,
                       'Water Temp Alarm': None,
                       'Helium Temp Alarm': None,
                       'Phase/Fuse Alarm': None,
                       'Motor Temp Alarm': None,
                       'System ON': None,
                       }

    def update(self, d):
        self.__Lock.acquire()
        if 'Helium Return Pressure' in d:
            self.return_pressure = d['Helium Return Pressure']
        if 'Helium Discharge Temperature' in d:
            self.helium_temp = d['Helium Discharge Temperature']
        if 'Water Inlet Temperature' in d:
            self.water_in_temp = d['Water Inlet Temperature']
        if 'Water Outlet Temperature' in d:
            self.water_out_temp = d['Water Outlet Temperature']
        if 'Firmware Version' in d:
            self.firmware_version = d['Firmware Version']
        if 'Operating Hours Elapsed' in d:
            self.op_hours = d['Operating Hours Elapsed']
        if 'RS-232 Config' in d:
            self.rs232_config = d['RS-232 Config']
        if 'Solenoid ON' in d:
            self.status['Solenoid ON'] = d['Solenoid ON']
        if 'Pressure Alarm' in d:
            self.status['Pressure Alarm'] = d['Pressure Alarm']
        if 'Oil Level Alarm' in d:
            self.status['Oil Level Alarm'] = d['Oil Level Alarm']
        if 'Water Flow Alarm' in d:
            self.status['Water Flow Alarm'] = d['Water Flow Alarm']
        if 'Water Temp Alarm' in d:
            self.status['Water Temp Alarm'] = d['Water Temp Alarm']
        if 'Helium Temp Alarm' in d:
            self.status['Helium Temp Alarm'] = d['Helium Temp Alarm']
        if 'Phase/Fuse Alarm' in d:
            self.status['Phase/Fuse Alarm'] = d['Phase/Fuse Alarm']
        if 'Motor Temp Alarm' in d:
            self.status['Motor Temp Alarm'] = d['Motor Temp Alarm']
        if 'System ON' in d:
            self.status['System ON'] = d['System ON']
        if 'Op-State' in d:
            self.op_state = d['Op-State']
        self.__Lock.release()

    def getVal(self, name):
        self.__Lock.acquire()
        if name == 'Helium Return Pressure':
            val = self.return_pressure
        elif name == 'Helium Discharge Temperature':
            val = self.helium_temp
        elif name == 'Water Inlet Temperature':
            val = self.water_in_temp
        elif name == 'Water Outlet Temperature':
            val = self.water_out_temp
        elif name == 'Firmware Version':
            val = self.firmware_version
        elif name == 'Operating Hours Elapsed':
            val = self.op_hours
        elif name == 'RS-232 Config':
            val = self.rs232_config
        elif name == 'Solenoid ON':
            val = self.status['Solenoid ON']
        elif name == 'Pressure Alarm':
            val = self.status['Pressure Alarm']
        elif name == 'Oil Level Alarm':
            val = self.status['Oil Level Alarm']
        elif name == 'Water Flow Alarm':
            val = self.status['Water Flow Alarm']
        elif name == 'Water Temp Alarm':
            val = self.status['Water Temp Alarm']
        elif name == 'Helium Temp Alarm':
            val = self.status['Helium Temp Alarm']
        elif name == 'Phase/Fuse Alarm':
            val = self.status['Phase/Fuse Alarm']
        elif name == 'Motor Temp Alarm':
            val = self.status['Motor Temp Alarm']
        elif name == 'System ON':
            val = self.status['System ON']
        elif name == 'Op-State':
            val = self.op_state
        else:  # Unknown Value!
            val = None
        self.__Lock.release()
        return val

    def getJson(self):
        self.__Lock.acquire()
        message = ['"Helium Return Pressure (psig)":%s' % json.dumps(self.return_pressure),
                   '"Helium Discharge Temp (C)":%s' % json.dumps(self.helium_temp),
                   '"Water Inlet Temp (C)":%s' % json.dumps(self.water_in_temp),
                   '"Water Outlet Temp (C)":%s' % json.dumps(self.water_out_temp),
                   '"Firmware Version":%s' % json.dumps(self.firmware_version),
                   '"Operating Hours Elapsed":%s' % json.dumps(self.op_hours),
                   '"RS-232 Config":%s' % json.dumps(self.rs232_config),
                   '"Op-State":%s' % json.dumps(self.op_state),
                   '"Status":%s' % json.dumps(self.status),
                   ]
        self.__Lock.release()
        return '{' + ','.join(message) + '}'

    def get_json_plots(self):
        self.__Lock.acquire()
        message = ['"Helium Return Pressure (psig)":%s' % json.dumps(self.return_pressure),
                   '"Helium Discharge Temp (C)":%s' % json.dumps(self.helium_temp),
                   '"Water Inlet Temp (C)":%s' % json.dumps(self.water_in_temp),
                   '"Water Outlet Temp (C)":%s' % json.dumps(self.water_out_temp),
                   ]
        self.__Lock.release()
        return message
