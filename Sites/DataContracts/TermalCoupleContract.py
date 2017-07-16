class TermalCoupleContract:
    def __init__(self, d):
        self.termalCouple = d
        self.temp = 0
    def update(self, d):
        self.temp = d

    def getJson(self):
        message = []
        message.append('{"termalcouple":%s,' % self.termalCouple)
        message.append('"temp":%s}' % self.temp)
        return ''.join(message)
