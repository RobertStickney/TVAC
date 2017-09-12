class ThermalProfileContract:
    def CtoK(self,num):
        return num + 273.15

    def __init__(self, d):
        if 'thermalsetpoint' in d:
            self.thermalsetpoint = d['thermalsetpoint']
        else:
            self.zone = 0
        if 'tempgoal' in d:
            self.tempGoal = self.CtoK(d['tempgoal'])
        else:
            self.temp = 0
        if 'soakduration' in d:
            self.soakduration = d['soakduration']
        else:
            self.soakduration = 0
        if 'ramp' in d:
            self.ramp = d['ramp']
        else:
            self.ramp = 0
        self.duration = 0
        self.temp = 0
        self.hold = False
        self.heldTemp = 0

    def update(self, d):
        if 'tempgoal' in d: # all temperatures are in Kelven
            self.tempGoal = d['tempgoal']
        if 'soakduration' in d:
            self.soakduration = d['soakduration']
        if 'ramp' in d:
            self.ramp = d['ramp']
        if 'temp' in d:  # Derived value - all temperatures are in Kelven
            self.temp = d['temp']
        if 'duration' in d:  # Derived value
            self.duration = d['duration']


    def getJson(self):
        message = []
        message.append('{"thermalsetpoint":%s,'% self.thermalsetpoint)
        message.append('"tempgoal":%s,' % self.tempGoal)
        message.append('"temp":%s,'%self.temp)
        message.append('"soakduration":%s,'%self.soakduration)
        message.append('"duration":%s,'%self.duration)
        message.append('"ramp":%s}'%self.ramp)
        return ''.join(message)
