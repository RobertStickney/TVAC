from StepContract import StepContract


class ZoneProfileContract:
    def __init__(self, d):
        if 'zone' in d:
            self.zoneID = d['zone']
        else:
            self.zone = 0
        if 'Average' in d:
            self.average = d['Average']
        else:
            self.Average = 0
        if 'steps' in d:
            self.steps = self.setSteps(d['steps'])
        else:
            self.duration = ''
        if 'ramp' in d:
            self.ramp = d['ramp']
        else:
            self.ramp = ''

    def setSteps(self,steps):
        list = []
        for step in steps:
            list.append(StepContract(step))
        return list

    def update(self, d):
        if 'zone' in d:
            self.zone = d['zone']
        if 'steps' in d:
            self.steps = self.setSteps(d['steps'])