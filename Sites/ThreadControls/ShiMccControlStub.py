#!/usr/bin/env python3.5
from threading import Thread
import time
import json
import os
import sys

if __name__ == '__main__':
    sys.path.insert(0, os.getcwd())

from Collections.ShiCryopumpInstance import ShiCryopumpInstance
from Shi_Cryo_Pump.Shi_Mcc import Shi_Mcc

from Logging.Logging import Logging


class ShiMccControlStub(Thread):
    def __init__(self, parent=None, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        Thread.__init__(self, group=group, target=target, name=name)
        self.args = args
        self.kwargs = kwargs
        self.parent = parent

        self.mcc = Shi_Mcc()
        self.hw = HardwareStatusInstance.getInstance()
        self.mcc_read_period = 0.5  # 0.5s loop period
        self.param_period = 30  # 10 second period

    def run(self):
        while True:

            # While true to restart the thread if it errors out
            try:
                # Thread "Start up" stuff goes here
                Logging.logEvent("Event", "Thread Start",
                                 {"thread": "Shi Mcc Control Stub"})
                Logging.logEvent("Debug", "Status Update",
                                 {"message": "Starting Shi Mcc Control Stub Thread",
                                  "level": 2})

                userName = os.environ['LOGNAME']
                if "root" in userName:
                    Logging.logEvent("Debug", "Status Update",
                                     {"message": "Power on restart of  Shi Mcc Control Stub Thread",
                                      "level": 3})
                    startup_delay = self.hw.PC_104.digital_out.getVal('MCC2 Power')
                    self.hw.PC_104.digital_out.update({'MCC2 Power': True})
                    if not startup_delay:
                        time.sleep(5)
                    # Now send some initialization commands
                    # The maximum second stage temperature the cryopump may start to restart after a power failure.
                    val = self.mcc.Set_RegenParam('6', 65)
                    if val['Error']:
                        Logging.logEvent("Debug", "Shi MCC Error",
                                         {"message": "Set_RegenParam: %s" % val['Response'],
                                          "level": 3})
                        raise Exception("Shi MCC Error with Set_RegenParam: %s" % val['Response'])
                    # 2: Power failure recovery enabled only when T2 is less than the limit set point.
                    val = self.mcc.Set_PowerFailureRecovery(2)
                    if val['Error']:
                        Logging.logEvent("Debug", "Shi MCC Error",
                                         {"message": "Set_RegenParam: %s" % val['Response'],
                                          "level": 3})
                        raise Exception("Shi MCC Error with Set_RegenParam: %s" % val['Response'])

                next_param_read_time = time.time()
                while True:
                    next_mcc_read_time = time.time() + self.mcc_read_period
                    if "root" in userName:
                        try:
                            Logging.logEvent("Debug", "Status Update",
                                             {"message": "Reading and writing with ShiMccControlStub.",
                                              "level": 4})
                            val = self.mcc.get_Status()
                            if val['Error']:
                                Logging.logEvent("Debug", "Shi MCC",
                                                 {"message": "response: %s" % val['Response'],
                                                  "level": 4})
                            else:
                                self.shi.cryopump.update({'MCC Params': val['Response']})
                            if time.time() > next_param_read_time:
                                val = self.mcc.get_ParamValues()
                                if val['Error']:
                                    Logging.logEvent("Debug", "Shi MCC",
                                                     {"message": "response: %s" % val['Response'],
                                                      "level": 4})
                                else:
                                    self.shi.cryopump.update({'MCC Params': val['Response']})
                                next_param_read_time = time.time() + self.param_period
                        except ValueError as err:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            Logging.logEvent("Error", 'Error in ShiMccControlStub reading values: "%s"' % err,
                                             {"type": exc_type,
                                              "filename": fname,
                                              "line": exc_tb.tb_lineno,
                                              "thread": "ShiMccControlStub"
                                              })
                    else:
                        Logging.logEvent("Debug", "Status Update",
                                         {"message": "Test run of Shi MCC loop",
                                          "level": 4})

                    if time.time() < next_mcc_read_time:
                        time.sleep(next_mcc_read_time - time.time())

            except Exception as e:
                # FileCreation.pushFile("Error",self.zoneUUID,'{"errorMessage":"%s"}'%(e))
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                Logging.logEvent("Error", "Shi MCC Interface Thread",
                                 {"type": exc_type,
                                  "filename": fname,
                                  "line": exc_tb.tb_lineno,
                                  "thread": "ShiMccControlStub"
                                  })
                Logging.logEvent("Debug", "Status Update",
                                 {"message": "There was a {} error in ShiMccControlStub. File: {}:{}\n{}".format(
                                     exc_type, fname, exc_tb.tb_lineno, e),
                                  "level": 2})
                # nicely close things, to open them back up again...
                userName = os.environ['LOGNAME']
                if "root" in userName:
                    pass
                # raise e
                time.sleep(4)

if __name__ == '__main__':
    # adding debug info
    if(len(sys.argv)>1):
        for arg in sys.argv:
            if arg.startswith("-v"):
                Logging.verbos = arg.count("v")
    Logging.logEvent("Debug","Status Update",
        {"message": "Debug on: Level {}".format(Logging.verbos),
         "level":1})
    thread = ShiMccControlStub()
    thread.daemon = True
    thread.start()

    shi_cp = ShiCryopumpInstance.getInstance()
    while True:
        time.sleep(2)
        print(shi_cp.cryopump.getJson())

