import os
import sys
import time
from threading import Thread

if __name__ == '__main__':
    sys.path.insert(0, os.getcwd())

from Collections.PC_104_Instance import PC_104_Instance
from Hardware_Drivers.TS_Registers import TS_Registers
from Hardware_Drivers.PWM_Square_Wave import PWM_Square_Wave
from Collections.HardwareStatusInstance import HardwareStatusInstance

from Logging.Logging import Logging


class TsRegistersUpdater(Thread):

    def __init__(self,parent=None, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        Thread.__init__(self, group=group, target=target, name=name)
        self.args = args
        self.kwargs = kwargs

        self.ts_reg = TS_Registers()
        self.da_io = PC_104_Instance.getInstance()
        self.hw = HardwareStatusInstance.getInstance()
        self.adc_period = 0.0125  # adc_clock*8 = 0.1s loop period
        self.pwm_period = 10  # 10 second pwm period
        # self.pwm_min_dc_sec = 1  # minimum Duty Cycle of 1 second
        self.ir_lamp_pwm = []
        self.time_test = time.time()
        self.parent = parent

    def run(self):
        while True:
            # While true to restart the thread if it errors out
            try:
                # Thread "Start up" stuff goes here
                Logging.logEvent("Debug","Status Update", 
                {"message": "Starting TS Registers Control Stub Thread",
                 "level":2,
                 })

                self.ir_lamp_pwm_start()
                
                if os.name == "posix":
                    userName = os.environ['LOGNAME']
                else:
                    userName = "user" 
                if "root" in userName:
                    # Root is only in live, might need to change in busy box
                    self.ts_reg.open_Registers()
                    self.da_io.digital_out.update(self.ts_reg.dio_read4(1, False))
                    self.da_io.digital_out.update(self.ts_reg.dio_read4(2, False))
                    self.da_io.digital_in.update(self.ts_reg.dio_read4(1))
                    self.da_io.digital_in.update(self.ts_reg.dio_read4(2))
                    time.sleep(1)
                    self.time_test = time.time()
                    # self.ts_reg.start_adc(1, 7, int(32e6 * self.adc_period))
                    self.ts_reg.start_adc(1, 7, 4000000)

                while True:
                    for i in range(len(self.ir_lamp_pwm)):
                        self.ir_lamp_pwm[i].update_waveform_state(self.da_io.digital_out.get_IR_Lamps_pwm_dc(i + 1))
                    if "root" in userName:
                        
                        Logging.logEvent("Debug","Status Update", 
                           {"message": "Reading and writing with PC 104",
                             "level":4})

                        self.interlocks()
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
                        # self.read_analog_in()  # loop period is adc_period * 2 seconds
                        self.wait_for_next_Multipule(self.adc_period * 8)
                    else:
                        Logging.logEvent("Debug","Status Update", 
                           {"message": "Test run of PC 104 loop",
                             "level":5})
                        time.sleep(5)

            except Exception as e:
                # FileCreation.pushFile("Error",self.zoneUUID,'{"errorMessage":"%s"}'%(e))
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                Logging.logEvent("Error","Hardware Interface Thread", 
                        {"type": exc_type,
                         "filename": fname,
                         "line": exc_tb.tb_lineno,
                         "thread": "TsRegistersUpdater"
                        })
                Logging.logEvent("Debug","Status Update", 
                        {"message": "There was a {} error in TsRegistersUpdater. File: {}:{}\n{}".format(exc_type,fname,exc_tb.tb_lineno,e),
                         "level":2})
                if Logging.debug:
                    raise e
                
                # nicely close things, to open them back up again...
                if os.name == "posix":
                    userName = os.environ['LOGNAME']
                else:
                    userName = "user" 
                if "root" in userName:
                    self.ts_reg.close()
                time.sleep(4)
                #raise (e)

    def wait_for_next_Multipule(self, m):  # m in seconds
        sleep_time = self.time_test - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)
        self.time_test += m
        Logging.debugPrint(6, "Ts Registers Sleep Time: {:0.6f}s".format(sleep_time))

    def read_analog_in(self):
        (first_channel, fifo_depth) = self.ts_reg.adc_fifo_status()
        Logging.debugPrint(4, "FIFO depth: {:d};  First Ch: {:d};  Time: {:0.6f}s".format(fifo_depth,
                                                                                first_channel,
                                                                                time.time()-self.time_test))
        self.time_test = time.time()
        if fifo_depth < 16:
            waitTime = self.adc_period * (8 - int(fifo_depth / 2))
            time.sleep(waitTime)
            (first_channel, fifo_depth) = self.ts_reg.adc_fifo_status()
            Logging.debugPrint(4, "FIFO depth: {:d}\twaitTime: {}".format(fifo_depth,waitTime))
        d = {}
        for n in range(fifo_depth):
            d['ADC ' + str((n + first_channel) % 16)] = self.ts_reg.adc_fifo_read()
        Logging.debugPrint(6,d)
        self.da_io.analog_in.update(d)

    def ir_lamp_pwm_start(self):
        self.ir_lamp_pwm = []
        offsets = [.1,.1, .2,.2, .3,.3, .4,.4, .5,.5, .6,.6, .7,.7, .8,.8]
        for i in range(16):
            self.ir_lamp_pwm.append(PWM_Square_Wave(self.pwm_period,
                                                    offsets[i],
                                                    "IR Lamp "+str(i+1),
                                                    self.da_io.digital_out.update))

    def interlocks(self):
        arc_cutoff_pressure_high = 10  # 10 Torr
        arc_cutoff_pressure_low = 40e-3  # 40 mTorr == 40e-3 Torr == 4e-2 Torr == 0.04 Torr
        MinRoughingPressure = 20e-3  # TODO: Change back to 8e-4 when done testing
        maxCrossoverPressure = 40e-3  # 40 mTorr

        cryoPumpPressure = self.hw.PfeifferGuages.get_cryopump_pressure()
        chamberPressure = self.hw.PfeifferGuages.get_chamber_pressure()
        # roughPumpPressure = self.hw.PfeifferGuages.get_roughpump_pressure()

        ChamberPowerLockout = True if (chamberPressure is None) or \
                                      ((chamberPressure > arc_cutoff_pressure_low) and
                                       (chamberPressure < arc_cutoff_pressure_high)) else False
        if ChamberPowerLockout:  # Disallow heaters when chamber is at low dielectric pressure.
            self.da_io.digital_out.update({'C1 B2': 0x00})  # IR lamp 1-8
            self.da_io.digital_out.update({'C1 B3': 0x00})  # IR lamp 9-16

        if self.hw.VacuumState is not None:
            if self.da_io.digital_in.getVal('Chamber_Closed'):
                if not self.hw.OperationalVacuum:  # Disallow heaters when not at operational vacuum.
                    self.da_io.digital_out.update({'C1 B2': 0x00})  # IR lamp 1-8
                    self.da_io.digital_out.update({'C1 B3': 0x00})  # IR lamp 9-16
                if chamberPressure < MinRoughingPressure:
                    self.da_io.digital_out.update({'RoughP GateValve': False})
                if chamberPressure > maxCrossoverPressure:
                    self.da_io.digital_out.update({'CryoP GateValve': False})
                if chamberPressure < (cryoPumpPressure*0.1):
                    self.da_io.digital_out.update({'CryoP GateValve': False})
                if not self.hw.PC_104.digital_in.getVal('CryoP_GV_Closed'):
                    self.da_io.digital_out.update({'RoughP GateValve': False})
                if self.da_io.digital_out.getVal('RoughP GateValve'):
                    self.da_io.digital_out.update({'CryoP GateValve': False})
            else:  # Chamber is open Debug state.
                pass

    def ir_lamp_pwm_stop(self):
        self.ir_lamp_pwm = []


if __name__ == '__main__':

    # adding debug info
    if(len(sys.argv)>1):
        for arg in sys.argv:
            if arg.startswith("-v"):
                Logging.verbos = arg.count("v")

    thread = TsRegistersUpdater()
    thread.daemon = True
    thread.start()

