class ThermalProfileContract:
    def __init__(self, d):
        if 'termalsetpoint' in d:
            self.termalsetpoint = d['termalsetpoint']
        else:
            self.zone = 0
        if 'tempgoal' in d:
            self.tempGoal = d['tempgoal']
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
        message.append('{"termalsetpoint":%s,'% self.termalsetpoint)
        message.append('"tempgoal":%s,' % self.tempGoal)
        message.append('"temp":%s,'%self.temp)
        message.append('"soakduration":%s,'%self.soakduration)
        message.append('"duration":%s,'%self.duration)
        message.append('"ramp":%s}'%self.ramp)
        return ''.join(message)
