class StepContract:
    def __init__(self, d):
        if 'Step' in d:
            self.stepID = d['Step']
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
        if 'ThermalCouples' in d:
            self.thermalCouples = d['ThermalCouples']
        else:
            self.ThermalCouples = []
        self.temp = 0

    def update(self, d):
        if d.stepID > 0:
            self.stepID = d.stepID
        if d.tempGoal:
            self.tempGoal = d.tempGoal
        if d.temp:
            self.temp = d.temp
        if d.duration:
            self.duration = d.duration
        if d.ramp:
            self.ramp = d.ramp
        if d.thermalCouples:
            self.thermalCouples = d.thermalCouples