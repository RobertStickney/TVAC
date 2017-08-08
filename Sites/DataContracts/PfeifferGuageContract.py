class PfeifferGuageContract:
    def __init__(self, Address, ParmDict, PressureDict):
        self.PfeifferGuage = Address
        self.parm41 = None  # Thinking for this is -> assign none so that if it does not update and
        self.parm49 = None  # an attempt is made to collect a value and add it to the json
        self.parm303 = None  # an error is thrown
        self.parm312 = None
        self.parm349 = None
        self.parm730 = None
        self.parm732 = None
        self.parm740 = None
        self.parm741 = None
        self.parm742 = None
        self.pressure = None




    def GetAddress(self):
        return self.PfeifferGuage

    def UpdateParm(self, ParmDict):
        self.parm41 = ParmDict['041']
        self.parm49 = ParmDict['049']
        self.parm303 = ParmDict['303']
        self.parm303 = ParmDict['312']
        self.parm349 = ParmDict['349']
        self.parm730 = ParmDict['730']
        self.parm732 = ParmDict['732']
        self.parm740 = ParmDict['740']
        self.parm741 = ParmDict['741']
        self.parm742 = ParmDict['742']

    def UpdatePressure(self, PressureDict):
        self.pressure = PressureDict['pressure']

    def getJson(self):
        message = []
        message.append('{"Address":%s,' % self.PfeifferGuage)
        message.append('{"041":%s,' % self.parm41)
        message.append('{"049":%s,' % self.parm49)
        message.append('{"303":%s,' % self.parm303)
        message.append('{"313":%s,' % self.parm312)
        message.append('{"349":%s,' % self.parm349)
        message.append('{"730":%s,' % self.parm730)
        message.append('{"732":%s,' % self.parm732)
        message.append('{"740":%s,' % self.parm740)
        message.append('{"741":%s,' % self.parm741)
        message.append('{"742":%s,' % self.parm742)
        message.append('{"pressure":%s,' % self.pressure)
        return ''.join(message)











