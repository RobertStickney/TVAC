class ThermocoupleContract:
    def __init__(self, d):
        self.Thermocouple = d
        self.temp = 0
        self.valid = False
        self.time = 0
        self.ctlZone = []

    def update(self, d):
        if 'temp' in d: # all temperatures are in Kelven
            self.temp = d['temp']
        if 'valid' in d:
            self.valid = d['valid']
        if 'time' in d:  # time offset from start of scan
            self.time = d['time']

    def getNum(self):
        return self.Thermocouple

    def getJson(self):
        message = []
        message.append('{"thermocouple":%s,' % self.Thermocouple)
        message.append('"time":%s}' % self.time)
        message.append('"temp":%s}' % self.temp)
        message.append('"valid":%s}' % self.valid)
        return ''.join(message)
