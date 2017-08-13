
class AnalogInContract:
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

    def getJson(self):
        message = []
        message.append('{"cabinetTemp1":%s,' % self.cabinetTemp1)
        message.append('"cabinetTemp2":%s,' % self.cabinetTemp2)
        message.append('"cabinetTemp3":%s,' % self.cabinetTemp3)
        #message.append('"notUsed1":%s,' % self.notUsed1) uncomment when this is used
        message.append('"fsFrontDoor1":%s,' % self.fsFrontDoor1)
        message.append('"fsFrontDoor2":%s,' % self.fsFrontDoor2)
        message.append('"fsFrontDoor3":%s,' % self.fsFrontDoor3)
        message.append('"fsBackDoor1":%s,' % self.fsBackDoor1)
        message.append('"fsBackDoor2":%s,' % self.fsBackDoor2)
        message.append('"fsBackDoor3":%s,' % self.fsBackDoor3)
        message.append('"pgRoughTemp":%s,' % self.pgRoughTemp)
        message.append('"pgChamber":%s,' % self.pgChamber)
        message.append('"pgCrypPump":%s,' % self.pgCrypPump)
        message.append('"pgRoughPump":%s,' % self.pgRoughPump)
        message.append('"LN2platen":%s,' % self.LN2platen)
        message.append('"LN2shroud":%s}' % self.LN2shroud)
        return ''.join(message)
