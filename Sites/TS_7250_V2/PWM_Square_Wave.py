#!/usr/bin/env python3.5
import time

from HouseKeeping.globalVars import debugPrint


class PWM_Square_Wave:

    # Period must be >= 1 sec
    def __init__(self, period, offset, min_duty_cycle=0.0, update_key='', update_fun=None):
        self.period = round(period, 1)  # in seoonds
        if period < 1: # seconds
            raise RuntimeError("PWM square wave period must be greater than 1 second, currently: {}".format(period))
        self.min_dc = self.coerce_to_range(min_duty_cycle, 0.0, 0.99999)
        self.duty_cycle = self.min_dc
        self.time_for_next_edge = round(time.time(), 1) + round(offset, 1)
        self.time_last_rising_edge = round(time.time(), 1)
        self.next_edge_is_rising = True
        self.waveform_state = False
        self.update_key = update_key
        self.update_bit_fun = update_fun

    def update_waveform_state(self, duty_cycle=None):
        if duty_cycle is not None:
            duty_cycle = self.coerce_to_range(duty_cycle, self.min_dc)
            if self.waveform_state and (duty_cycle < self.duty_cycle):
                self.time_for_next_edge = self.time_last_rising_edge + round(self.period * duty_cycle, 1)
            self.duty_cycle = duty_cycle
        debugPrint(4,"Key {:}: {:f}".format(self.update_key, self.duty_cycle))
        if time.time() >= self.time_for_next_edge:
            if self.next_edge_is_rising:
                self.time_last_rising_edge = round(time.time(), 1)
                self.time_last_rising_edge = round(time.time(), 1)
                if self.duty_cycle <= self.min_dc:
                    self.time_for_next_edge = self.time_last_rising_edge + self.period
                    self.waveform_state = False
                elif self.duty_cycle == 1:
                    self.time_for_next_edge = self.time_last_rising_edge + self.period
                    self.waveform_state = True
                else:
                    self.time_for_next_edge = self.time_last_rising_edge + round(self.period * duty_cycle, 1)
                    self.waveform_state = True
                    self.next_edge_is_rising = False
            else:
                self.time_for_next_edge = self.time_last_rising_edge + self.period
                self.waveform_state = False
                self.next_edge_is_rising = True
            if self.update_bit_fun is not None:
                self.update_bit_fun({self.update_key: self.waveform_state})
        if self.update_bit_fun is None:
            return self.waveform_state

    def coerce_to_range(self, value, min_val=0.0, max_val=1.0):
        if value > max_val:
            val = max_val
        elif value < min_val:
            val = min_val
        else:
            val = value
        return val


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '../')
    from DataContracts.DigitalOutContract import DigitalOutContract

    d_out = DigitalOutContract()
    numbers = [1, 2]
    offsets = [.4,.9]
    duty_cycles = [0, 1]
    pwm_wf = []
    for i in range(len(numbers)):
        pwm_wf.append(PWM_Square_Wave(5, offsets[i], 0, "IR Lamp "+str(numbers[i]), d_out.update))
        d_out.update({"IR Lamp " + str(numbers[i]) + " PWM DC": duty_cycles[i]})
        print("Duty Cycle {:d}: {:f}".format(numbers[i], d_out.get_IR_Lamps_pwm_dc(numbers[i])))
    start_time = round(time.time(), 2)

    for n in range(200):
        for i in range(len(numbers)):
            pwm_wf[i].update_waveform_state(d_out.get_IR_Lamps_pwm_dc(numbers[i]))
        print("b2: {:x}; \tb2: {:x}; \tTime: {:04.2f}".format(d_out.get_c1_b2(),
                                                              d_out.get_c1_b3(),
                                                              time.time()-start_time))
        if n == 120:
            duty_cycles = [.5, .4]
            for i in range(len(numbers)):
                # ---->> Use this as an example for updating PWM. <<----
                d_out.update({"IR Lamp " + str(numbers[i]) + " PWM DC": duty_cycles[i]})
        time.sleep(.1)

