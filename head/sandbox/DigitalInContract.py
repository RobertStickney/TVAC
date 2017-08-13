
class DigitalInContract:
    def __init__(self):
        self.pgRoughPumpRelay1 = False  # C 1: Di 0 - Roughing Pump Pressure Gauge Relay 1
        self.pgRoughPumpRelay2 = False  # C 1: Di 1 - Roughing Pump Pressure Gauge Relay 2
        self.pgCryoPumpRelay1 = False   # C 1: Di 2 - Cryo-pump Pressure Gauge Relay 1
        self.pgCryoPumpRelay2 = False   # C 1: Di 3 - Cryo-pump Pressure Gauge Relay 2
        self.pgChamberRelay1 = False    # C 1: Di 4 - Chamber Pressure Gauge Relay 1
        self.pgChamberRelay2 = False    # C 1: Di 5 - Chamber Pressure Gauge Relay 2
        self.t1 = False                 # C 1: Di 6 -
        self.t2 = False                 # C 1: Di 7 -
        self.t3 = False                 # C 1: Di 8 -
        self.t4 = False                 # C 1: Di 9 -
        self.t5 = False                 # C 1: Di 10-
        self.t6 = False                 # C 1: Di 11-
        self.t7 = False                 # C 1: Di 12-
        self.t8 = False                 # C 1: Di 13-
        self.t9 = False                 # C 1: Di 14-
        self.t10 = False                # C 1: Di 15-
        self.t11 = False                # C 1: Di 16-
        self.t12 = False                # C 1: Di 17-
        self.t13 = False                # C 1: Di 18-
        self.t14 = False                # C 1: Di 19-
        self.t15 = False                # C 1: Di 20-
        self.t16 = False                # C 1: Di 21-
        self.t17 = False                # C 1: Di 22-
        self.t18 = False                # C 1: Di 23-
        self.notUsed1 = False           # C 1: Di 24- Unassigned channel 24
        self.notUsed2 = False           # C 1: Di 25- Unassigned channel 25
        self.notUsed3 = False           # C 1: Di 26- Unassigned channel 26
        self.notUsed4 = False           # C 1: Di 27- Unassigned channel 27
        self.notUsed5 = False           # C 1: Di 28- Unassigned channel 28
        self.notUsed6 = False           # C 1: Di 29- Unassigned channel 29
        self.LN2AirOK = False           # C 1: Di 30- 100 psi Air supply connected to the LN2 supply valves
        self.AirOK = False              # C 1: Di 31- 100 psi Air supply connected to the TVAC
        self.t20 = False                # C 2: Di 0 -
        self.t21 = False                # C 2: Di 1 -
        self.t22 = False                # C 2: Di 2 -
        self.t23 = False                # C 2: Di 3 -
        self.t24 = False                # C 2: Di 4 -
        self.t25 = False                # C 2: Di 5 -
        self.t26 = False                # C 2: Di 6 -
        self.t27 = False                # C 2: Di 7 -
        self.t28 = False                # C 2: Di 8 -
        self.t29 = False                # C 2: Di 9 -
        self.t30 = False                # C 2: Di 10-
        self.t31 = False                # C 2: Di 11-
        self.t32 = False                # C 2: Di 12-
        self.t33 = False                # C 2: Di 13-
        self.t34 = False                # C 2: Di 14-
        self.t35 = False                # C 2: Di 15-
        self.t36 = False                # C 2: Di 16-
        self.t37 = False                # C 2: Di 17-
        self.t38 = False                # C 2: Di 18-
        self.t39 = False                # C 2: Di 19-
        self.t40 = False                # C 2: Di 20-
        self.t41 = False                # C 2: Di 21-
        self.t42 = False                # C 2: Di 22-
        self.t43 = False                # C 2: Di 23-
        self.t44 = False                # C 2: Di 24-
        self.t45 = False                # C 2: Di 25-
        self.t46 = False                # C 2: Di 26-
        self.t47 = False                # C 2: Di 27-
        self.t48 = False                # C 2: Di 28-
        self.t49 = False                # C 2: Di 29-
        self.t50 = False                # C 2: Di 30-
        self.LN2en = False              # C 2: Di 31- LN2 flow is enabled

    def update(self, d):
        if 'C1 B0' in d:
            self.pgRoughPumpRelay1 = ((d['C1 B0'] & 0x01) > 0)  # C 1: Di 1
            self.pgRoughPumpRelay2 = ((d['C1 B0'] & 0x02) > 0)  # C 1: Di 1
            self.pgCryoPumpRelay1 = ((d['C1 B0'] & 0x04) > 0)  # C 1: Di 2
            self.pgCryoPumpRelay2 = ((d['C1 B0'] & 0x08) > 0)  # C 1: Di 3
            self.pgChamberRelay1 = ((d['C1 B0'] & 0x10) > 0)  # C 1: Di 4
            self.pgChamberRelay2 = ((d['C1 B0'] & 0x20) > 0)  # C 1: Di 5
            self.t1 = ((d['C1 B0'] & 0x40) > 0)  # C 1: Di 6
            self.t2 = ((d['C1 B0'] & 0x80) > 0)  # C 1: Di 7
        if 'C1 B1' in d:
            self.t3 = ((d['C1 B1'] & 0x01) > 0)  # C 1: Di 8
            self.t4 = ((d['C1 B1'] & 0x02) > 0)  # C 1: Di 9
            self.t5 = ((d['C1 B1'] & 0x04) > 0)  # C 1: Di 10
            self.t6 = ((d['C1 B1'] & 0x08) > 0)  # C 1: Di 11
            self.t7 = ((d['C1 B1'] & 0x10) > 0)  # C 1: Di 12
            self.t8 = ((d['C1 B1'] & 0x20) > 0)  # C 1: Di 13
            self.t9 = ((d['C1 B1'] & 0x40) > 0)  # C 1: Di 14
            self.t10 = ((d['C1 B1'] & 0x80) > 0)  # C 1: Di 15
        if 'C1 B2' in d:
            self.t11 = ((d['C1 B2'] & 0x01) > 0)  # C 1: Di 16
            self.t12 = ((d['C1 B2'] & 0x02) > 0)  # C 1: Di 17
            self.t13 = ((d['C1 B2'] & 0x04) > 0)  # C 1: Di 18
            self.t14 = ((d['C1 B2'] & 0x08) > 0)  # C 1: Di 19
            self.t15 = ((d['C1 B2'] & 0x10) > 0)  # C 1: Di 20
            self.t16 = ((d['C1 B2'] & 0x20) > 0)  # C 1: Di 21
            self.t17 = ((d['C1 B2'] & 0x40) > 0)  # C 1: Di 22
            self.t18 = ((d['C1 B2'] & 0x80) > 0)  # C 1: Di 23
        if 'C1 B3' in d:
            self.notUsed1 = ((d['C1 B3'] & 0x01) > 0)  # C 1: Di 24
            self.notUsed2 = ((d['C1 B3'] & 0x02) > 0)  # C 1: Di 25
            self.notUsed3 = ((d['C1 B3'] & 0x04) > 0)  # C 1: Di 26
            self.notUsed4 = ((d['C1 B3'] & 0x08) > 0)  # C 1: Di 27
            self.notUsed5 = ((d['C1 B3'] & 0x10) > 0)  # C 1: Di 28
            self.notUsed6 = ((d['C1 B3'] & 0x20) > 0)  # C 1: Di 29
            self.LN2AirOK = ((d['C1 B3'] & 0x40) > 0)  # C 1: Di 30
            self.AirOK = ((d['C1 B3'] & 0x80) > 0)  # C 1: Di 31
        if 'C2 B0' in d:
            self.t20 = ((d['C2 B0'] & 0x01) > 0)  # C 2: Di 0
            self.t21 = ((d['C2 B0'] & 0x02) > 0)  # C 2: Di 1
            self.t22 = ((d['C2 B0'] & 0x04) > 0)  # C 2: Di 2
            self.t23 = ((d['C2 B0'] & 0x08) > 0)  # C 2: Di 3
            self.t24 = ((d['C2 B0'] & 0x10) > 0)  # C 2: Di 4
            self.t25 = ((d['C2 B0'] & 0x20) > 0)  # C 2: Di 5
            self.t26 = ((d['C2 B0'] & 0x40) > 0)  # C 2: Di 6
            self.t27 = ((d['C2 B0'] & 0x80) > 0)  # C 2: Di 7
        if 'C2 B1' in d:
            self.t28 = ((d['C2 B1'] & 0x01) > 0)  # C 2: Di 8
            self.t29 = ((d['C2 B1'] & 0x02) > 0)  # C 2: Di 9
            self.t30 = ((d['C2 B1'] & 0x04) > 0)  # C 2: Di 10
            self.t31 = ((d['C2 B1'] & 0x08) > 0)  # C 2: Di 11
            self.t32 = ((d['C2 B1'] & 0x10) > 0)  # C 2: Di 12
            self.t33 = ((d['C2 B1'] & 0x20) > 0)  # C 2: Di 13
            self.t34 = ((d['C2 B1'] & 0x40) > 0)  # C 2: Di 14
            self.t35 = ((d['C2 B1'] & 0x80) > 0)  # C 2: Di 15
        if 'C2 B2' in d:
            self.t36 = ((d['C2 B2'] & 0x01) > 0)  # C 2: Di 16
            self.t37 = ((d['C2 B2'] & 0x02) > 0)  # C 2: Di 17
            self.t38 = ((d['C2 B2'] & 0x04) > 0)  # C 2: Di 18
            self.t39 = ((d['C2 B2'] & 0x08) > 0)  # C 2: Di 19
            self.t40 = ((d['C2 B2'] & 0x10) > 0)  # C 2: Di 20
            self.t41 = ((d['C2 B2'] & 0x20) > 0)  # C 2: Di 21
            self.t42 = ((d['C2 B2'] & 0x40) > 0)  # C 2: Di 22
            self.t43 = ((d['C2 B2'] & 0x80) > 0)  # C 2: Di 23
        if 'C2 B3' in d:
            self.t44 = ((d['C2 B3'] & 0x01) > 0)  # C 2: Di 24
            self.t45 = ((d['C2 B3'] & 0x02) > 0)  # C 2: Di 25
            self.t46 = ((d['C2 B3'] & 0x04) > 0)  # C 2: Di 26
            self.t47 = ((d['C2 B3'] & 0x08) > 0)  # C 2: Di 27
            self.t48 = ((d['C2 B3'] & 0x10) > 0)  # C 2: Di 28
            self.t49 = ((d['C2 B3'] & 0x20) > 0)  # C 2: Di 29
            self.t50 = ((d['C2 B3'] & 0x40) > 0)  # C 2: Di 30
            self.LN2en = ((d['C2 B3'] & 0x80) > 0)  # C 2: Di 31

    def getJson(self):
        message = []
        message.append('{"pgRoughPumpRelay1":%s,' % self.pgRoughPumpRelay1)
        message.append('"pgRoughPumpRelay2":%s,' % self.pgRoughPumpRelay2)
        message.append('"pgCryoPumpRelay1":%s,' % self.pgCryoPumpRelay1)
        message.append('"pgCryoPumpRelay2":%s,' % self.pgCryoPumpRelay2)
        message.append('"pgChamberRelay1":%s,' % self.pgChamberRelay1)
        message.append('"pgChamberRelay2":%s,' % self.pgChamberRelay2)
        #message.append('"t1":%s,' % self.t1) uncomment when this is used
        #message.append('"notUsed1":%s,' % self.notUsed1) uncomment when this is used
        message.append('"LN2AirOK":%s,' % self.LN2AirOK)
        message.append('"AirOK":%s,' % self.AirOK)
        #message.append('"t20":%s,' % self.t20) uncomment when this is used
        message.append('"LN2en":%s}' %self.LN2en)
        return ''.join(message)
