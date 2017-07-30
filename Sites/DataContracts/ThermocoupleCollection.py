import datetime, json

from DataContracts.ThermocoupleContract import ThermocoupleContract

class ThermocoupleCollection:

    def __init__(self, Num = 120):
        self.tcList = self.buildCollection(Num)
        self.time = datetime.now()
        self.ValidTCs = []
        self.InvalidTCs = []
        for tc in self.tcList:
            self.updateValidTCs(tc)


    def buidCollection(self, Num):
        TCs = []
        for i in range(1, Num+1):
            TCs.append = ThermocoupleContract(i)
        return TCs

    def update(self, d):
        if 'time' in d:
            self.time = d['time']
        for updateTC in d['tcList']:
            tc = self.getTC(updateTC['Thermocouple'])
            tc.update(updateTC)
            self.updateValidTCs(tc)

    def getTC(self, n):
        for tc in self.tcList:
            if tc.Thermocouple == n:
                return tc
        raise RuntimeError('Thermocouple #: %s is out of range' % n)


    def updateValidTCs(self, tc):
        if tc.valid:
            if tc in self.InvalidTCs:
                self.InvalidTCs.remove(tc)
            if tc not in self.ValidTCs:
                self.ValidTCs.append(tc)
        else:
            if tc in self.ValidTCs:
                self.ValidTCs.remove(tc)
            if tc not in self.InvalidTCs:
                self.InvalidTCs.append(tc)

    def getJson(self, whichTCs = 'all'):
        message = []
        message.append('"time":%s}' % self.time)
        if whichTCs == 'valid':
            message.append('TCs:%s' % json.dumps([tc.getJson() for tc in self.ValidTCs]))
        elif whichTCs == 'invalid':
            message.append('TCs:%s' % json.dumps([tc.getJson() for tc in self.InvalidTCs]))
        else:
            message.append('TCs:%s' % json.dumps([tc.getJson() for tc in self.tcList]))

        return ''.join(message)

if __name__ == '__main__':
    tcColl = ThermocoupleCollection(5)
    tcColl.updateValidTCs()
