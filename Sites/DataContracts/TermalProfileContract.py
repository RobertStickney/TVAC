class TermalProfileContract:
    def __init__(self, d):
        if 'TermalSetPoint' in d:
            self.termalsetpoint = d['TermalSetPoint']
        else:
            self.zone = 0
        if 'TempGoal' in d:
            self.tempGoal = d['TempGoal']
        else:
            self.temp = 0
        if 'GoalDuration' in d:
            self.goalDuration = d['GoalDuration']
        else:
            self.goalDuration = 0
        if 'Ramp' in d:
            self.ramp = d['Ramp']
        else:
            self.ramp = 0
        self.duration = 0
        self.temp = 0
        self.hold = False
        self.heldTemp = 0

    def update(self, d):
        if 'TempGoal' in d:
            self.tempGoal = d['TempGoal']
        if 'GoalDuration' in d:
            self.goalDuration = d['GoalDuration']
        if 'Ramp' in d:
            self.ramp = d['Ramp']
        if 'temp' in d:
            self.temp = d['temp']
        if 'duration' in d:
            self.duration = d['duration']

    def getJson(self):
        message = []
        message.append('{"termalsetpoint":%s,'% self.termalsetpoint)
        message.append('"tempgoal":%s,' % self.tempGoal)
        message.append('"temp":%s,'%self.temp)
        message.append('"goalduration":%s,'%self.goalDuration)
        message.append('"duration":%s,'%self.duration)
        message.append('"ramp":%s}'%self.ramp)
        return ''.join(message)
