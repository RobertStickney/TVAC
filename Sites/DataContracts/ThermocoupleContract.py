class ThermocoupleContract:
    def __init__(self, d):
        self.Thermocouple = d
        self.temp = 0
        self.working = False
        self.time = 0
        self.alarm = 0

    def update(self, d):
        if 'time' in d:  # time offset from start of scan
            self.time = d['time']
        if 'temp' in d: # all temperatures are in Kelven
            self.temp = d['temp']
        if 'working' in d:
            self.working = d['working']
        if 'alarm' in d:
            self.alarm = d['alarm']

    def getNum(self):
        return self.Thermocouple

    def getTemp(self, temp_units = 'K'):
        # temp_units values: ['K', 'C', 'F']
        if temp_units == 'C':
            return self.temp - 273.15
        elif temp_units == 'F':
            return (self.temp - 273.15)*9/5 + 32
        else:
            return self.temp


def getJson(self, temp_units = 'K'):
        # temp_units values: ['K', 'C', 'F']
        message = []
        message.append('{"thermocouple":%s,' % self.Thermocouple)
        message.append('"time":%s}' % self.time)
        message.append('"temp":%s}' % self.getTemp(temp_units))
        message.append('"working":%s}' % self.working)
        return ''.join(message)
