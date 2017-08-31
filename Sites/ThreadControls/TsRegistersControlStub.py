from threading import Thread
import json
import uuid
import time
import datetime
import os

from HardwareStatusInstance import HardwareStatusInstance
from TS_7250_V2.TS_Registers import TS_Registers


class TsRegistersControlStub(Thread):

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        Thread.__init__(self, group=group, target=target, name=name)
        self.args = args
        self.kwargs = kwargs

        self.ts_reg = TS_Registers()
        # TODO CHANGE ME self.da_io = PC_104_Instance.getInstance()
        self.updatePeriod = 0.2 # in seconds

    def run(self):
        print('TsRegistersControlStub PID: {:d}  Parent PID: {:d}'.format(os.getpid(), os.getppid()))
        try:
            self.ts_reg.open_Registers()
            self.da_io.digital_out.update(self.ts_reg.dio_read4(1, False))
            self.da_io.digital_out.update(self.ts_reg.dio_read4(2, False))

            while os.getppid() != 1:  # Exit when parent thread stops running
                self.ts_reg.do_write4([self.da_io.digital_out.c1_b0,
                                       self.da_io.digital_out.c1_b1,
                                       self.da_io.digital_out.c1_b2,
                                       self.da_io.digital_out.c1_b3], 1)
                self.ts_reg.do_write4([self.da_io.digital_out.c2_b0,
                                       self.da_io.digital_out.c2_b1,
                                       self.da_io.digital_out.c2_b2,
                                       self.da_io.digital_out.c2_b3], 2)
                if self.da_io.digital_out.RoughP_Start:
                    self.da_io.digital_out.update({"RoughP Start":False})
                self.da_io.digital_in.update(self.ts_reg.dio_read4(1))
                self.da_io.digital_in.update(self.ts_reg.dio_read4(2))
                self.ts_reg.dac_write(self.da_io.analog_out.dac_counts[2], 2)
                self.ts_reg.dac_write(self.da_io.analog_out.dac_counts[3], 3)
                time.sleep(self.updatePeriod)

            self.ts_reg.close()
            print('Closed the mmaps!')
        except Exception as e:
            #FileCreation.pushFile("Error",self.zoneUUID,'{"errorMessage":"%s"}'%(e))
            print('Error accessing the PC104 Bus. Error: %s' % e)
        return







