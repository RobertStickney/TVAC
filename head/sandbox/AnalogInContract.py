
class AnalogInContract:

    __Lock = threading.RLock()

    def __init__(self):
        self.cabinetTemp1 = 0  # ADC 0 - Cabinet Temperature Sensor 1
        self.cabinetTemp2 = 0  # ADC 1 - Cabinet Temperature Sensor 2
        self.CabinetTemp3 = 0  # ADC 2 - Cabinet Temperature Sensor 3
        self.notUsed1 = 0      # ADC 3 - Unassigned channel 3
        self.fsFrontDoor1 = 0  # ADC 4 - Front Door Force Sensor #1
        self.fsFrontDoor2 = 0  # ADC 5 - Front Door Force Sensor #2
        self.fsFrontDoor3 = 0  # ADC 6 - Front Door Force Sensor #3
        self.fsBackDoor1 = 0   # ADC 7 - Back Door Force Sensor #1
        self.fsBackDoor2 = 0   # ADC 8 - Back Door Force Sensor #2
        self.fsBackDoor3 = 0   # ADC 9 - Back Door Force Sensor #3
        self.pgRoughTemp = 0   # ADC 10- Temperature of the Roughing Pump PT1000 Sensor
        self.pgChamber = 0     # ADC 11- Pfeiffer gauge Analog Pressure Reading for the chamber
        self.pgCrypPump = 0    # ADC 12- Pfeiffer gauge Analog Pressure Reading for the Cryp-Pump
        self.pgRoughPump = 0   # ADC 13- Pfeiffer gauge Analog Pressure Reading for the Roughing Pump
        self.LN2platen = 0     # ADC 14- Platen LN2 Supply Valve Position 4-20mA
        self.LN2shroud = 0     # ADC 14- Shroud LN2 Supply Valve Position 4-20mA

    def update(self, d):
        self.__Lock.acquire()
        if 'ADC 0' in d:
            self.cabinetTemp1 = d['ADC 0']  # todo: add conversion to value from ADC counts
        if 'ADC 1' in d:
            self.cabinetTemp2 = d['ADC 1']  # todo: add conversion to value from ADC counts
        if 'ADC 2' in d:
            self.cabinetTemp3 = d['ADC 2']  # todo: add conversion to value from ADC counts
        if 'ADC 3' in d:
            self.notUsed1 = d['ADC 3']  # todo: add conversion to value from ADC counts
        if 'ADC 4' in d:
            self.fsFrontDoor1 = d['ADC 4']  # todo: add conversion to value from ADC counts
        if 'ADC 5' in d:
            self.fsFrontDoor2 = d['ADC 5']  # todo: add conversion to value from ADC counts
        if 'ADC 6' in d:
            self.fsFrontDoor3 = d['ADC 6']  # todo: add conversion to value from ADC counts
        if 'ADC 7' in d:
            self.fsBackDoor1 = d['ADC 7']  # todo: add conversion to value from ADC counts
        if 'ADC 8' in d:
            self.fsBackDoor2 = d['ADC 8']  # todo: add conversion to value from ADC counts
        if 'ADC 9' in d:
            self.fsBackDoor3 = d['ADC 9']  # todo: add conversion to value from ADC counts
        if 'ADC 10' in d:
            self.pgRoughTemp = d['ADC 10']  # todo: add conversion to value from ADC counts
        if 'ADC 11' in d:
            self.pgChamber = d['ADC 11']  # todo: add conversion to value from ADC counts
        if 'ADC 12' in d:
            self.pgCrypPump = d['ADC 12']  # todo: add conversion to value from ADC counts
        if 'ADC 13' in d:
            self.pgRoughPump = d['ADC 13']  # todo: add conversion to value from ADC counts
        if 'ADC 14' in d:
            self.LN2platen = d['ADC 14']  # todo: add conversion to value from ADC counts
        if 'ADC 15' in d:
            self.LN2shroud = d['ADC 15']  # todo: add conversion to value from ADC counts
        self.__Lock.release()

    def get_cabinetTemp1(self):
        self.__Lock.acquire()
        val = self.cabinetTemp1
        self.__Lock.release()
        return val

    def get_cabinetTemp2(self):
        self.__Lock.acquire()
        val = self.cabinetTemp2
        self.__Lock.release()
        return val

    def get_cabinetTemp3(self):
        self.__Lock.acquire()
        val = self.cabinetTemp3
        self.__Lock.release()
        return val

    def get_notUsed1(self):
        self.__Lock.acquire()
        val = self.notUsed1
        self.__Lock.release()
        return val

    def get_fsFrontDoor1(self):
        self.__Lock.acquire()
        val = self.fsFrontDoor1
        self.__Lock.release()
        return val

    def get_fsFrontDoor2(self):
        self.__Lock.acquire()
        val = self.fsFrontDoor2
        self.__Lock.release()
        return val

    def get_fsFrontDoor3(self):
        self.__Lock.acquire()
        val = self.fsFrontDoor3
        self.__Lock.release()
        return val

    def get_fsBackDoor1(self):
        self.__Lock.acquire()
        val = self.fsBackDoor1
        self.__Lock.release()
        return val

    def get_fsBackDoor2(self):
        self.__Lock.acquire()
        val = self.fsBackDoor2
        self.__Lock.release()
        return val

    def get_fsBackDoor3(self):
        self.__Lock.acquire()
        val = self.fsBackDoor3
        self.__Lock.release()
        return val

    def get_pgRoughTemp(self):
        self.__Lock.acquire()
        val = self.pgRoughTemp
        self.__Lock.release()
        return val

    def get_pgChamber(self):
        self.__Lock.acquire()
        val = self.pgChamber
        self.__Lock.release()
        return val

    def get_pgCrypPump(self):
        self.__Lock.acquire()
        val = self.pgCrypPump
        self.__Lock.release()
        return val

    def get_pgRoughPump(self):
        self.__Lock.acquire()
        val = self.pgRoughPump
        self.__Lock.release()
        return val

    def get_LN2platen(self):
        self.__Lock.acquire()
        val = self.LN2platen
        self.__Lock.release()
        return val

    def get_LN2shroud(self):
        self.__Lock.acquire()
        val = self.LN2shroud
        self.__Lock.release()
        return val

    def getJson(self):
        self.__Lock.acquire()
        message = []
        message.append('{"Cabinet Temp 1":%s,' % self.cabinetTemp1)
        message.append('"Cabinet Temp 2":%s,' % self.cabinetTemp2)
        message.append('"Cabinet Temp 3":%s,' % self.cabinetTemp3)
        message.append('"notUsed1":%s,' % self.notUsed1)
        message.append('"fs Front Door 1":%s,' % self.fsFrontDoor1)
        message.append('"fs Front Door 2":%s,' % self.fsFrontDoor2)
        message.append('"fs Front Door 3":%s,' % self.fsFrontDoor3)
        message.append('"fs Back Door 1":%s,' % self.fsBackDoor1)
        message.append('"fs Back Door 2":%s,' % self.fsBackDoor2)
        message.append('"fs Back Door 3":%s,' % self.fsBackDoor3)
        message.append('"Rough Pump Temp":%s,' % self.pgRoughTemp)
        message.append('"pg Chamber":%s,' % self.pgChamber)
        message.append('"pg Cryp Pump":%s,' % self.pgCrypPump)
        message.append('"pg Rough Pump":%s,' % self.pgRoughPump)
        message.append('"LN2 platen":%s,' % self.LN2platen)
        message.append('"LN2 shroud":%s}' % self.LN2shroud)
        self.__Lock.release()
        return ''.join(message)
