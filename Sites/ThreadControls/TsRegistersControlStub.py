from threading import Thread
import time
import os

from Collections.PC_104_Instance import PC_104_Instance
from TS_7250_V2.TS_Registers import TS_Registers
from TS_7250_V2.PWM_Square_Wave import PWM_Square_Wave
from HouseKeeping.globalVars import debugPrint


class TsRegistersControlStub(Thread):

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        Thread.__init__(self, group=group, target=target, name=name)
        self.args = args
        self.kwargs = kwargs

        self.ts_reg = TS_Registers()
        self.da_io = PC_104_Instance.getInstance()
        self.adc_period = 0.0125  # adc_clock*8 = 0.1s loop period
        self.pwm_period = 30  # 30 second pwm period
        self.pwm_min_dc = 1  # minimum Duty Cycle of 1 second
        self.ir_lamp_pwm = []
        self.time_test = time.time()

    def run(self):
        debugPrint(2,"Starting TS Registers Control Stub Thread")
        userName = os.environ['LOGNAME']

        try:
            # This should be done both inside and outside of testing
            self.ir_lamp_pwm_start()
            if "root" in userName:
                self.ts_reg.open_Registers()
                self.da_io.digital_out.update(self.ts_reg.dio_read4(1, False))
                self.da_io.digital_out.update(self.ts_reg.dio_read4(2, False))
                time.sleep(2)
                self.time_test = time.time()
                self.ts_reg.start_adc(1, 7, int(32e6 * self.adc_period))

            while True:
                # This should be done both inside and outside of testing
                for i in range(len(self.ir_lamp_pwm)):
                    self.ir_lamp_pwm[i].update_waveform_state(self.da_io.digital_out.get_IR_Lamps_pwm_dc(i+1))
                if "root" in userName:
                    debugPrint(5,"Reading and writing with PC 104")
                    self.ts_reg.do_write4([self.da_io.digital_out.get_c1_b0(),
                                           self.da_io.digital_out.get_c1_b1(),
                                           self.da_io.digital_out.get_c1_b2(),
                                           self.da_io.digital_out.get_c1_b3()], 1)
                    self.ts_reg.do_write4([self.da_io.digital_out.get_c2_b0(),
                                           self.da_io.digital_out.get_c2_b1(),
                                           self.da_io.digital_out.get_c2_b2(),
                                           self.da_io.digital_out.get_c2_b3()], 2)
                    if self.da_io.digital_out.getVal('RoughP Start'):
                        self.da_io.digital_out.update({'RoughP Start': False})
                    self.da_io.digital_in.update(self.ts_reg.dio_read4(1))
                    self.da_io.digital_in.update(self.ts_reg.dio_read4(2))
                    self.ts_reg.dac_write(self.da_io.analog_out.get_dac_counts(2), 2)
                    self.ts_reg.dac_write(self.da_io.analog_out.get_dac_counts(3), 3)
                    self.read_analog_in()  # loop period is adc_period * 2 seconds
                else:
                    debugPrint(4, "Blank loop while testing: PC 104 loop")
                    time.sleep(self.adc_period*8)

            self.ir_lamp_pwm_stop()
            self.ts_reg.close()
            debugPrint(3,'Closed the mmaps!')
        except Exception as e:
            # FileCreation.pushFile("Error",self.zoneUUID,'{"errorMessage":"%s"}'%(e))
            print('Error accessing the PC104 Bus. Error: %s' % e)
            raise e
        return

    def read_analog_in(self):
        (first_channel, fifo_depth) = self.ts_reg.adc_fifo_status()
        debugPrint(4, "FIFO depth: {:d};  First Ch: {:d};  Time: {:0.3f}s".format(fifo_depth,
                                                                                first_channel,
                                                                                time.time()-self.time_test))
        self.time_test = time.time()
        while fifo_depth < 16:
            debugPrint(4,"FIFO depth: {:d}".format(fifo_depth))
            time.sleep(self.adc_period * int(8 - (fifo_depth / 2)))
            (first_channel, fifo_depth) = self.ts_reg.adc_fifo_status()
        d = {}
        for n in range(fifo_depth):
            d['ADC ' + str((n + first_channel) % 16)] = self.ts_reg.adc_fifo_read()
        debugPrint(6,d)
        # self.da_io.analog_in.update(d)

    def ir_lamp_pwm_start(self):
        self.ir_lamp_pwm = []
        offsets = [.1,.1, .2,.2, .3,.3, .4,.4, .5,.5, .6,.6, .7,.7, .8,.8]
        for i in range(16):
            self.ir_lamp_pwm.append(PWM_Square_Wave(self.pwm_period,
                                                    offsets[i],
                                                    self.pwm_min_dc,
                                                    "IR Lamp "+str(i+1),
                                                    self.da_io.digital_out.update))

    def ir_lamp_pwm_stop(self):
        self.ir_lamp_pwm = []

if __name__ == '__main__':
    import sys
    sys.path.insert(0, '../')
    thread = TsRegistersControlStub()
    thread.daemon = True
    thread.start()

