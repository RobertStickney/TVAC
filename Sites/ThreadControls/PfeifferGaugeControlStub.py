#!/usr/bin/env python3.5
from threading import Thread
import time

import os
import sys

if __name__ == '__main__':
    sys.path.insert(0, os.getcwd())

from Collections.HardwareStatusInstance import HardwareStatusInstance
from Collections.ProfileInstance import ProfileInstance
from PfeifferGuage.PfeifferGauge import PfeifferGauge

from Logging.MySql import MySQlConnect
from Logging.Logging import Logging


class PfeifferGaugeControlStub(Thread):
    def __init__(self, parent=None, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        Thread.__init__(self, group=group, target=target, name=name)
        self.args = args
        self.kwargs = kwargs
        self.parent = parent

        self.zoneProfiles = ProfileInstance.getInstance().zoneProfiles
        self.Pgauge = PfeifferGauge()
        self.gauges = HardwareStatusInstance.getInstance().PfeifferGuages
        self.pressure_read_peroid = 0.5  # 0.5s loop period
        self.param_period = 5  # 5 second period

    def logPressureData(self):
        coloums = "( profile_I_ID, guage, pressure )"
        values  = "( \"{}\",{},{} ),\n".format(self.zoneProfiles.profileUUID, 1, self.gauges.get_pressure_chamber())
        values += "( \"{}\",{},{} ),\n".format(self.zoneProfiles.profileUUID, 2, self.gauges.get_pressure_cryopump())
        values += "( \"{}\",{},{} )".format(self.zoneProfiles.profileUUID, 3, self.gauges.get_pressure_roughpump())
        sql = "INSERT INTO tvac.Pressure {} VALUES {};".format(coloums, values)
        # print(sql)
        mysql = MySQlConnect()
        try:
            mysql.cur.execute(sql)
            mysql.conn.commit()
        except Exception as e:
            raise e
            #return e

    def run(self):
        '''
        '''
        # used for testing
        first = True
        while True:
            # While true to restart the thread if it errors out
            try:
                # Thread "Start up" stuff goes here
                Logging.logEvent("Event", "Thread Start",
                                 {"thread": "Pfeiffer Guage Control Stub"})
                Logging.logEvent("Debug", "Status Update",
                                 {"message": "Starting Pfeiffer Guage Control Stub Thread",
                                  "level": 2})

                userName = os.environ['LOGNAME']
                if "root" in userName:
                    self.read_all_params()
                next_pressure_read_time = time.time()
                next_param_read_time = time.time()
                while True:
                    next_pressure_read_time += self.pressure_read_peroid
                    if "root" in userName:
                        try:
                            self.gauges.update([{'addr': 1, 'Pressure': self.Pgauge.GetPressure(1)},
                                                {'addr': 2, 'Pressure': self.Pgauge.GetPressure(2)},
                                                {'addr': 3, 'Pressure': self.Pgauge.GetPressure(3)}])
                            Logging.logEvent("Debug", "Status Update",
                                             {"message": "Reading and writing with PfeifferGaugeControlStub.\n1: {:f}; 2: {:f}; 3: {:f}; ".format(
                                                 self.Pgauge.GetPressure(1),
                                                 self.Pgauge.GetPressure(2),
                                                 self.Pgauge.GetPressure(3)
                                             ),
                                              "level": 4})
                            if time.time() > next_param_read_time:
                                self.gauges.update([{'addr': 1, 'error': self.Pgauge.GetError(1),
                                                                'cc on': self.Pgauge.GetCCstate(1)},
                                                    {'addr': 2, 'error': self.Pgauge.GetError(2),
                                                                'cc on': self.Pgauge.GetCCstate(2)},
                                                    {'addr': 3, 'error': self.Pgauge.GetError(3)}])
                                next_param_read_time += self.param_period
                        except ValueError as err:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            Logging.logEvent("Error", 'Error in PfeifferGaugeControlStub reading values: "%s"' % err,
                                             {"type": exc_type,
                                              "filename": fname,
                                              "line": exc_tb.tb_lineno,
                                              "thread": "PfeifferGaugeControlStub"
                                              })
                    else:
                        Logging.logEvent("Debug", "Status Update",
                                         {"message": "Test run of Pfeiffer Guages loop",
                                          "level": 4})
                        if first:
                            # TODO: Test the system at differnt starting pressures, it could restart at any point
                            # What happens when pressure in roughing  is more than cryo?
                            self.gauges.update([{'addr': 1, 'Pressure': 1000},
                                                {'addr': 2, 'Pressure': 1},
                                                {'addr': 3, 'Pressure': 999}])
                            first = False
                        else:
                            self.gauges.update([{'addr': 1, 'Pressure': self.gauges.get_pressure_cryopump()/2.5},
                                                {'addr': 2, 'Pressure': self.gauges.get_pressure_chamber()/5},
                                                {'addr': 3, 'Pressure': self.gauges.get_pressure_roughpump()/3}])
                        # Just to see the screen for longer
                        time.sleep(5)

                    Logging.logEvent("Debug", "Status Update",
                             {"message": "Current Pressure in Chamber is {}".format(self.gauges.get_pressure_chamber()),
                              "level": 3})
                    if __name__ != '__main__':
                        self.logPressureData()
                    if time.time() < next_pressure_read_time:
                        time.sleep(next_pressure_read_time - time.time())

            except Exception as e:
                # FileCreation.pushFile("Error",self.zoneUUID,'{"errorMessage":"%s"}'%(e))
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                Logging.logEvent("Error", "Pfeiffer Interface Thread",
                                 {"type": exc_type,
                                  "filename": fname,
                                  "line": exc_tb.tb_lineno,
                                  "thread": "PfeifferGaugeControlStub"
                                  })
                Logging.logEvent("Debug", "Status Update",
                                 {"message": "There was a {} error in PfeifferGaugeControlStub. File: {}:{}\n{}".format(
                                     exc_type, fname, exc_tb.tb_lineno, e),
                                  "level": 2})
                # raise e
            # nicely close things, to open them back up again...
            finally:
                userName = os.environ['LOGNAME']
                if "root" in userName:
                    pass
                time.sleep(4)

    def read_all_params(self):
        paramslist = [{'addr': 1,
                       'Model Name': self.Pgauge.GetModelName(1),
                       'Software Vir': self.Pgauge.GetSofwareV(1),
                       'CC sw mode': self.Pgauge.GetSwMode(1),
                       'Pressure SP 1': self.Pgauge.GetSwPressure(1, True),
                       'Pressure SP 2': self.Pgauge.GetSwPressure(1, False),
                       'Pirani Correction': self.Pgauge.GetCorrPir(1),
                       'CC Correction': self.Pgauge.GetCorrCC(1)},
                      {'addr': 2,
                       'Model Name': self.Pgauge.GetModelName(2),
                       'Software Vir': self.Pgauge.GetSofwareV(2),
                       'CC sw mode': self.Pgauge.GetSwMode(2),
                       'Pressure SP 1': self.Pgauge.GetSwPressure(2, True),
                       'Pressure SP 2': self.Pgauge.GetSwPressure(2, False),
                       'Pirani Correction': self.Pgauge.GetCorrPir(2),
                       'CC Correction': self.Pgauge.GetCorrCC(2)},
                      {'addr': 3,
                       'Model Name': self.Pgauge.GetModelName(3),
                       'Software Vir': self.Pgauge.GetSofwareV(3),
                       'Pressure SP 1': self.Pgauge.GetSwPressure(3, True),
                       'Pressure SP 2': self.Pgauge.GetSwPressure(3, False),
                       'Pirani Correction': self.Pgauge.GetCorrPir(3)}]
        self.gauges.update(paramslist)

if __name__ == '__main__':
    # adding debug info
    if(len(sys.argv)>1):
        for arg in sys.argv:
            if arg.startswith("-v"):
                Logging.verbos = arg.count("v")
    Logging.logEvent("Debug","Status Update",
        {"message": "Debug on: Level {}".format(Logging.verbos),
         "level":1})
    thread = PfeifferGaugeControlStub()
    thread.daemon = True
    thread.start()

    p = HardwareStatusInstance.getInstance().PfeifferGuages
    while True:
        time.sleep(2)
        # print(p.getJson())
        print("1:{:f}".format(p.get_pressure_chamber()))
        print("2:{:f}".format(p.get_pressure_cryopump()))
        print("3:{:f}".format(p.get_pressure_roughpump()))
