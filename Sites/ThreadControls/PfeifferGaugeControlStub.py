#!/usr/bin/env python3.5
from threading import Thread
import time

import os

# if __name__ == '__main__':
#     import sys
#     sys.path.insert(0, '../')

from Collections.PfeifferGaugeInstance import PfeifferGaugeInstance
from PfeifferGuage.PfeifferGauge import PfeifferGauge

from Logging.Logging import Logging


class PfeifferGaugeControlStub(Thread):
    def __init__(self, parent=None, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        Thread.__init__(self, group=group, target=target, name=name)
        self.args = args
        self.kwargs = kwargs
        self.parent = parent

        self.Pgauge = PfeifferGauge()
        self.pressure = PfeifferGaugeInstance.getInstance()
        self.pressure_read_peroid = 0.5  # 0.5s loop period
        self.param_period = 5  # 10 second period

    def run(self):
        while True:
            # While true to restart the thread if it errors out
            try:
                # Thread "Start up" stuff goes here
                Logging.logEvent("Event", "Thread Start",
                                 {"thread": "Pfeiffer Guage Control Stub"})
                Logging.logEvent("Debug", "Status Update",
                                 {"message": "Starting Pfeiffer Guage Control Stub Thread",
                                  "level": 2})

                self.read_all_params()
                next_pressure_read_time = time.time() + self.pressure_read_peroid
                next_param_read_time = time.time() + self.param_period
                userName = os.environ['LOGNAME']
                if "root" in userName:
                    # Root is only in live, might need to change in busy box
                    pass

                while True:
                    self.parent.safetyThread.heartbeats["TsRegistersControlStub"] = time.time()
                    if "root" in userName:
                        try:
                            Logging.logEvent("Debug", "Status Update",
                                             {"message": "Reading and writing with PC 104",
                                              "level": 5})
                            self.pressure.guages.update([{'addr': 1, 'Pressure': self.Pgauge.GetPressure(1)},
                                                         {'addr': 2, 'Pressure': self.Pgauge.GetPressure(2)},
                                                         {'addr': 3, 'Pressure': self.Pgauge.GetPressure(3)}])
                            if time.time() < next_param_read_time:
                                self.pressure.guages.update([{'addr': 1, 'error': self.Pgauge.GetError(1),
                                                                         'cc on': self.Pgauge.GetCCstate(1)},
                                                             {'addr': 2, 'error': self.Pgauge.GetError(2),
                                                                         'cc on': self.Pgauge.GetCCstate(3)},
                                                             {'addr': 3, 'error': self.Pgauge.GetError(3)}])
                                next_param_read_time = time.time() + self.param_period
                        except ValueError as err:
                            Logging.logEvent("Debug", "Status Update",
                                             {"message": 'Error in PfeifferGaugeControlStub reading values: "%s"' % err,
                                              "level": 2})
                    else:
                        Logging.logEvent("Debug", "Status Update",
                                         {"message": "Test run of Pfeiffer Guages loop",
                                          "level": 4})
                    if time.time() < next_pressure_read_time:
                        time.sleep(next_pressure_read_time - time.time())
                        next_pressure_read_time = time.time() + self.pressure_read_peroid

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
                # nicely close things, to open them back up again...
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
        self.pressure.guages.update(paramslist)

if __name__ == '__main__':
    import sys

    sys.path.insert(0, '../')
    thread = PfeifferGaugeControlStub()
    thread.daemon = True
    thread.start()

    p = PfeifferGaugeInstance.getInstance()
    while True:
        time.sleep(2)
        print(p.gauges.getJson)

