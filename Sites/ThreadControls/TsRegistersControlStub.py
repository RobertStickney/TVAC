from threading import Thread
import json
import uuid
import time
import datetime
import os

from Collections.PC_104_Instance import PC_104_Instance
from TS_7250_V2 import TS_Registers

from HouseKeeping.globalVars import debugPrint


class TsRegistersControlStub(Thread):

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        Thread.__init__(self, group=group, target=target, name=name)
        self.args = args
        self.kwargs = kwargs

        self.ts_reg = TS_Registers.TS_Registers()
        self.da_io = PC_104_Instance.getInstance()
        self.updatePeriod = 1.2 # in seconds

    def run(self):
        debugPrint(2,"Starting TS Registers Control Stub Thread")
        userName = os.environ['LOGNAME']

        try:
            if "root" in userName:
                self.ts_reg.open_Registers()
                self.da_io.digital_out.update(self.ts_reg.dio_read4(1, False))
                self.da_io.digital_out.update(self.ts_reg.dio_read4(2, False))

            while os.getppid() != 1:  # Exit when parent thread stops running
                # uncomment when on live system
                if "root" in userName:
                    debugPrint(3,"Reading and writing with PC 104")
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
                else:

                    debugPrint(4,"Blank loop while testing: PC 104 loop")
                time.sleep(self.updatePeriod)

            self.ts_reg.close()
            print('Closed the mmaps!')
        except Exception as e:
            #FileCreation.pushFile("Error",self.zoneUUID,'{"errorMessage":"%s"}'%(e))
            print('Error accessing the PC104 Bus. Error: %s' % e)
        return







