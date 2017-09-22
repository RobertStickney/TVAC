import threading
import json


class PfeifferGaugeContract:

    __lock = threading.RLock()

    def __init__(self, address, sys_location):
        self.address = address
        self.system_location = sys_location
        self.model_name = None
        self.model_name_cpt200 = False
        self.model_name_ppt200 = False
        self.model_name_rpt200 = False
        self.model_name_hpt200 = False
        self.model_name_mpt200 = False
        self.cold_cathode_on = None
        self.cc_overlap_switch = None
        self.actual_error = None  # an error is thrown
        self.software_version = None
        self.pressure_switch_point_1 = None
        self.pressure_switch_point_2 = None
        self.pressure = None
        self.pirani_correction_value = None
        self.cold_cathode_correction_value = None

    def GetAddress(self):
        return self.address

    def update(self, d):
        print(d)
        self.__lock.acquire()
        if 'Model Name' in d:
            self.model_name = d['Model Name']
            if self.model_name == 'CPT 200':
                self.model_name_cpt200 = True
                self.model_name_ppt200 = False
                self.model_name_rpt200 = False
                self.model_name_hpt200 = False
                self.model_name_mpt200 = False
                self.cold_cathode_on = None
                self.cc_overlap_switch = None
                self.pirani_correction_value = None
                self.cold_cathod_correction_value = None
            elif self.model_name == 'PPT 200':
                self.model_name_cpt200 = False
                self.model_name_ppt200 = True
                self.model_name_rpt200 = False
                self.model_name_hpt200 = False
                self.model_name_mpt200 = False
                self.cold_cathode_on = None
                self.cc_overlap_switch = None
                self.cold_cathod_correction_value = None
            elif self.model_name == 'RPT 200':
                self.model_name_cpt200 = False
                self.model_name_ppt200 = False
                self.model_name_rpt200 = True
                self.model_name_hpt200 = False
                self.model_name_mpt200 = False
                self.cold_cathode_on = None
                self.cold_cathod_correction_value = None
            elif self.model_name == 'HPT 200':
                self.model_name_cpt200 = False
                self.model_name_ppt200 = False
                self.model_name_rpt200 = False
                self.model_name_hpt200 = True
                self.model_name_mpt200 = False
            elif self.model_name == 'MPT 200':
                self.model_name_cpt200 = False
                self.model_name_ppt200 = False
                self.model_name_rpt200 = False
                self.model_name_hpt200 = False
                self.model_name_mpt200 = True
            else:
                self.model_name_cpt200 = False
                self.model_name_ppt200 = False
                self.model_name_rpt200 = False
                self.model_name_hpt200 = False
                self.model_name_mpt200 = False
        if 'Software Vir' in d:
            self.software_version = d['Software Vir']
        if ('cc on' in d) and (self.model_name_hpt200 or
                               self.model_name_mpt200):
            self.cold_cathode_on = d['cc on']
        if ('CC sw mode' in d) and (self.model_name_rpt200 or
                                    self.model_name_hpt200 or
                                    self.model_name_mpt200):
            self.cc_overlap_switch = d['CC sw mode']
        if 'error' in d:
            self.actual_error = d['error']
        if 'Pressure SP 1' in d:
            self.pressure_switch_point_1 = d['Pressure SP 1']
        if 'Pressure SP 2' in d:
            self.pressure_switch_point_2 = d['Pressure SP 2']
        if 'Pressure' in d:
            self.pressure = d['Pressure']  # in Torr
        if ('Pirani Correction' in d) and (self.model_name_ppt200 or
                                           self.model_name_rpt200 or
                                           self.model_name_hpt200 or
                                           self.model_name_mpt200):
            self.pirani_correction_value = d['Pirani Correction']
        if ('CC Correction' in d) and (self.model_name_hpt200 or
                                       self.model_name_mpt200):
            self.cold_cathod_correction_value = d['CC Correction']
        self.__lock.release()

    def getPressure(self):
        self.__lock.acquire()
        val = self.pressure
        self.__lock.release()
        return val

    def getPressureJson(self):
        self.__lock.acquire()
        message = ['{"Address":%s,' % self.address,
                   '"Pressure":%s}' % self.pressure]
        self.__lock.release()
        return ''.join(message)

    def getJson(self):
        self.__lock.acquire()
        message = ['{"Address":%s,' % self.address,
                   '"System Location":%s,' % self.system_location,
                   '"Pressure":%s,' % self.pressure,
                   '"Model Name":%s,' % self.model_name,
                   '"Software Version":%s,' % self.software_version,
                   '"Actual Error Code":%s,' % self.actual_error,
                   '"Pressure Switch Point 1":%s,' % self.pressure_switch_point_1,
                   '"Pressure Switch Point 2":%s,' % self.pressure_switch_point_2]
        if self.model_name_hpt200 or self.model_name_mpt200:
            message.append('"Cold Cathode On":%s,' % json.dumps(self.cold_cathode_on))
        if self.model_name_rpt200 or self.model_name_hpt200 or self.model_name_mpt200:
            message.append('"Cold Cathode Overlap Switch":%s,' % self.cc_overlap_switch)
        if self.model_name_ppt200 or self.model_name_rpt200 or self.model_name_hpt200 or self.model_name_mpt200:
            message.append('"Pirani Correction Value":%s,' % self.pirani_correction_value)
        if self.model_name_hpt200 or self.model_name_mpt200:
            message.append('"Cold Cathode Correction Value":%s}' % self.cold_cathode_correction_value)
        self.__lock.release()
        return ''.join(message)
