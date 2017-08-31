from threading import Thread
import json
import uuid
import time
import datetime
import os

from PC_104_Instance import PC_104_Instance
from Testing_mmap import TS_Registers


class TsRegistersControlStub(Thread):

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        Thread.__init__(self, group=group, target=target, name=name)
        self.args = args
        self.kwargs = kwargs

        self.ts_reg = TS_Registers()
        self.da_io = PC_104_Instance.getInstance()
        self.adc_period = 0.0125  # adc_clock*8 = 0.1s loop period
        self.pwm_period = 20  # seconds

    def run(self):
        print('TsRegistersControlStub PID: {:d}  Parent PID: {:d}'.format(os.getpid(), os.getppid()))
        try:
            self.ts_reg.open_Registers()
            self.ts_reg.start_adc(1, 7, int(32e6*self.adc_period))
            self.da_io.digital_out.update(self.ts_reg.dio_read4(1, False))
            self.da_io.digital_out.update(self.ts_reg.dio_read4(2, False))

            while os.getppid() != 1:  # Exit when parent thread stops running
                # self.ir_lamp_duty_cycle()
                self.ts_reg.do_write4([self.da_io.digital_out.get_c1_b0,
                                       self.da_io.digital_out.get_c1_b1,
                                       self.da_io.digital_out.get_c1_b2,
                                       self.da_io.digital_out.get_c1_b3], 1)
                self.ts_reg.do_write4([self.da_io.digital_out.get_c2_b0,
                                       self.da_io.digital_out.get_c2_b1,
                                       self.da_io.digital_out.get_c2_b2,
                                       self.da_io.digital_out.get_c2_b3], 2)
                if self.da_io.digital_out.RoughP_Start:
                    self.da_io.digital_out.update({"RoughP Start":False})
                self.da_io.digital_in.update(self.ts_reg.dio_read4(1))
                self.da_io.digital_in.update(self.ts_reg.dio_read4(2))
                self.ts_reg.dac_write(self.da_io.analog_out.dac_counts[2], 2)
                self.ts_reg.dac_write(self.da_io.analog_out.dac_counts[3], 3)
                self.read_analog_in()  #loop period is adc_period * 2 seconds

            self.ts_reg.close()
            print('Closed the mmaps!')
        except Exception as e:
            #FileCreation.pushFile("Error",self.zoneUUID,'{"errorMessage":"%s"}'%(e))
            print('Error accessing the PC104 Bus. Error: %s' % e)
        return

    def read_analog_in(self):
        (first_channel, fifo_depth) = self.ts_reg.adc_fifo_status()
        while fifo_depth < 16:
            print("FIFO depth: {:d}".format(fifo_depth))
            time.sleep(self.adc_period * ((fifo_depth / 2) - 8))
            (first_channel, fifo_depth) = self.ts_reg.adc_fifo_status()
        d = {}
        for n in range(fifo_depth):
            d['ADC ' + str((n + first_channel) % 16)] = self.ts_reg.adc_fifo_read()
        print(d)
        #self.da_io.analog_in.update(d)

    def ir_lamp_duty_cycle(self):
        for n in range(1, 16+1):
            pass





