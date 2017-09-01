import time

class PWM_Square_Wave():

    def __init__(self, period, offset, update_key, update_fun):
        self.period = round(period, 1)  # in seoonds
        self.duty_cycle = 0
        self.time_for_next_edge = round(time.time(), 1) + offset
        self.time_last_rising_edge = round(time.time(), 1)
        self.next_edge_is_rising = True
        self.waveform_state = False
        self.update_key = update_key
        self.update_bit_fun = update_fun

    def updade_waveform_state(self, duty_cycle=None):
        if duty_cycle is not None:
            duty_cycle = self.coerce_to_range(duty_cycle)
            if self.waveform_state and (duty_cycle < self.duty_cycle):
                self.time_for_next_edge = self.time_last_rising_edge + round(self.period * duty_cycle, 1)
            self.duty_cycle = duty_cycle
        if time.time() >= self.time_for_next_edge:
            if self.next_edge_is_rising:
                self.time_last_rising_edge = round(time.time(), 1)
                if self.duty_cycle == 0:
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
                self.waveform_state = True
                self.next_edge_is_rising = True
            print(str({self.update_key, self.waveform_state}))
            self.update_bit_fun({self.update_key, self.waveform_state})

    def coerce_to_range(self, value, min_val=0, max_val=1):
        if value > max_val:
            val = max_val
        elif value < min_val:
            val = min_val
        else:
            val = value
        return val