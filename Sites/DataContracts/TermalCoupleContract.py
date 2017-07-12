class TermalCoupleContract:
    def __init__(self, d):
        self.termalCouple = d
        self.temp = 0
    def update(self, d):
        self.temp = d
