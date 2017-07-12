class TermalProfileContract:
    def __init__(self, d):
        if 'TermalSetPoint' in d:
            self.stepID = d['TermalSetPoint']
        else:
            self.zone = 0
        if 'TempGoal' in d:
            self.tempGoal = d['TempGoal']
        else:
            self.temp = 0
        if 'GoalDuration' in d:
            self.duration = d['GoalDuration']
        else:
            self.duration = 0
        if 'Ramp' in d:
            self.ramp = d['Ramp']
        else:
            self.ramp = 0
        self.temp = 0

    def update(self, d):
        if 'TempGoal' in d:
            self.tempGoal = d['TempGoal']
        if 'GoalDuration' in d:
            self.duration = d['GoalDuration']
        if 'Ramp' in d:
            self.ramp = d['Ramp']
        if 'temp' in d:
            self.temp = d['temp']