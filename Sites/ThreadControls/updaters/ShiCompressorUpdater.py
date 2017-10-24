#!/usr/bin/env python3.5
import os
import sys
import time
from threading import Thread

if __name__ == '__main__':
    sys.path.insert(0, os.getcwd())

from Collections.HardwareStatusInstance import HardwareStatusInstance
from Collections.ProfileInstance import ProfileInstance
from Hardware_Drivers.Shi_Compressor import ShiCompressor

from Logging.Logging import Logging


class ShiCompressorUpdater(Thread):
    def __init__(self, parent=None, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        Thread.__init__(self, group=group, target=target, name=name)
        self.args = args
        self.kwargs = kwargs
        self.parent = parent

        self.compressor = ShiCompressor()
        self.hw = HardwareStatusInstance.getInstance()
        self.compressor_read_period = 1  # 0.5s loop period
        self.op_hours_read_period = 120  # 120s = 2 min read period

    def run(self):
        # While true to restart the thread if it errors out
        while True:
            # Catch anything that goes wrong
            # This has no check because it should always be running
            try:
                # Thread "Start up" stuff goes here
                # Logging.logEvent("Event", "Thread Start",
                #                 {"thread": "Shi Compressor Updater",
                #                 "ProfileInstance": ProfileInstance.getInstance()})
                Logging.logEvent("Debug", "Status Update",
                                {"message": "Starting Shi Compressor Updater",
                                "level": 2})

                if os.name == "posix":
                    userName = os.environ['LOGNAME']
                else:
                    userName = "user"
                if "root" in userName:
                    # Live systems go here
                    Logging.logEvent("Debug", "Status Update",
                                    {"message": "Power on the Shi Compressor",
                                    "level": 3})
                    self.compressor.open_port()
                    Currently_powered = self.hw.PC_104.digital_out.getVal('CryoP Pwr Relay 1')
                    self.hw.PC_104.digital_out.update({'CryoP Pwr Relay 1': True})
                    if not Currently_powered:
                        time.sleep(5)
                    self.compressor.flush_port()

                next_op_hours_read_time = time.time()
                # setup is done, this loop is the normal thread loop
                while True:
                    next_compressor_read_time = time.time() + self.compressor_read_period
                    if "root" in userName:
                        try:
                            Logging.logEvent("Debug", "Status Update",
                                             {"message": "Reading and writing with ShiCompressorUpdater.",
                                              "level": 4})
                            val = {}
                            val.update(self.compressor.get_temperatures())
                            val.update(self.compressor.get_pressure())
                            val.update(self.compressor.get_status_bits())
                            if time.time() > next_op_hours_read_time:
                                val.update(self.compressor.get_id())
                                next_op_hours_read_time += self.op_hours_read_period
                            self.hw.ShiCryopump.update({'Compressor': val})
                            Logging.logEvent("Debug", "Status Update",
                                             {"message": "Cryopump Stage 1: {:.1f}K; Stage 2: {:.1f}K"
                                                         "".format(self.hw.ShiCryopump.get_compressor('Stage 1 Temp'),
                                                                   self.hw.ShiCryopump.get_compressor('Stage 2 Temp')),
                                              "level": 4})

                            while len(self.hw.Shi_Compressor_Cmds):
                                cmd = self.hw.Shi_Compressor_Cmds.pop()
                                if 'on' == cmd:
                                    self.compressor.set_compressor_on()
                                elif 'off' == cmd:
                                    self.compressor.set_compressor_off()
                                elif 'reset' == cmd:
                                    self.compressor.set_reset()
                                else:
                                    Logging.logEvent("Error", 'Unknown Shi_Compressor_Cmds: "%s"' % cmd,
                                                     {"type": 'Unknown Shi_Compressor_Cmds',
                                                      "filename": 'ThreadControls/ShiCompressorUpdater.py',
                                                      "line": 0,
                                                      "thread": "ShiCompressorUpdater"
                                                      })
                        except ValueError as err:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            Logging.logEvent("Error", 'Error in ShiCompressorUpdater reading values: "%s"' % err,
                                             {"type": exc_type,
                                              "filename": fname,
                                              "line": exc_tb.tb_lineno,
                                              "thread": "ShiCompressorUpdater"
                                              })
                            raise err
                    else:
                        Logging.logEvent("Debug", "Status Update",
                                         {"message": "Test run of Shi Compressor loop",
                                          "level": 4})

                    if time.time() < next_compressor_read_time:
                        time.sleep(next_compressor_read_time - time.time())

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                Logging.logEvent("Error", "Shi Compressor Interface Thread",
                                 {"type": exc_type,
                                  "filename": fname,
                                  "line": exc_tb.tb_lineno,
                                  "thread": "ShiCompressorUpdater"
                                  })
                Logging.logEvent("Debug", "Status Update",
                                 {"message": "There was a {} error in ShiCompressorUpdater. File: {}:{}\n{}".format(
                                     exc_type, fname, exc_tb.tb_lineno, e),
                                  "level": 2})
                # raise e
                self.compressor.close_port()
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

    hw_status = HardwareStatusInstance.getInstance()
    hw_status.PC_104.digital_out.update({'CryoP Pwr Relay 1': True})

    thread = ShiCompressorUpdater()
    thread.daemon = True
    thread.start()

    while True:
        time.sleep(5)
        print(hw_status.ShiCryopump.getJson())

