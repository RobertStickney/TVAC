class ZoneContract:
    def __init__(self, d):
        if 'zone' in d:
            self.zone = d['zone']
        else:
            self.zone = 0
        if 'temp' in d:
            self.temp = d['temp']
        else:
            self.temp = ''
        if 'duration' in d:
            self.duration = d['duration']
        else:
            self.duration = ''
        if 'ramp' in d:
            self.ramp = d['ramp']
        else:
            self.ramp = ''

    def update(self, d):
        if d.zone > 0:
            self.zone = d.zone
        if 'temp' != '':
            self.temp = d.temp
        if 'duration' != '':
            self.duration = d.duration
        if 'ramp' != '':
            self.ramp = d.ramp