import threading


class AnalogOutContract:

    __updateLock = threading.RLock()

    def __init__(self):
        self.dac_counts = [0, 0, 0, 0]  # Dac counts
        self.notUsed1 = 0   # DAC 0 - Unassigned channel 1
        self.notUsed1 = 0   # DAC 1 - Unassigned channel 2
        self.LN2platen = 0  # DAC 2 - Platen LN2 Supply Valve Position
        self.LN2shroud = 0  # DAC 3 - Shroud LN2 Supply Valve Position

    def update(self, d):
        self.__updateLock.acquire()
        if 'notUsed1' in d:
            self.notUsed1 = d['notUsed1']
            self.dac_counts[0] = self.notUsed1  # todo: add conversion to value from ADC counts
        if 'notUsed2' in d:
            self.notUsed1 = d['notUsed2']
            self.dac_counts[1] = self.notUsed1  # todo: add conversion to value from ADC counts
        if 'LN2platen' in d:
            self.LN2platen = d['LN2platen']
            self.dac_counts[2] = self.LN2platen  # todo: add conversion to value from ADC counts
        if 'LN2shroud' in d:
            self.LN2shroud = d['LN2shroud']
            self.dac_counts[3] = self.LN2shroud  # todo: add conversion to value from ADC counts
        self.__updateLock.release()

    def getJson(self):
        message = []
        #message.append('"notUsed1":%s,' % self.notUsed1) uncomment when this is used
        message.append('"LN2platen":%s,' % self.LN2platen)
        message.append('"LN2shroud":%s}' % self.LN2shroud)
        return ''.join(message)
