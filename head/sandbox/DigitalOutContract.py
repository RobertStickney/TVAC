import threading


class DigitalOutContract:

    __updateLock = threading.RLock()

    def __init__(self):
        self.c1_b0 = 0x00               # C1: B0: Do0 - Do7
        self.c1_b1 = 0x00               # C1: B1: Do8 - Do15
        self.c1_b2 = 0x00               # C1: B2: Do16 - Do23
        self.c1_b3 = 0x00               # C1: B3: Do24 - Do31
        self.c2_b0 = 0x00               # C2: B0: Do0 - Do7
        self.c2_b1 = 0x00               # C2: B1: Do8 - Do15
        self.c2_b2 = 0x00               # C2: B2: Do16 - Do23
        self.c2_b3 = 0x00               # C2: B3: Do24 - Do31
        self.LN2_P_EN = False           # C 1: Do 0 -
        self.LN2_S_EN = False           # C 1: Do 1 -
        self.LN2_Sol_EN = False         # C 1: Do 2 -
        self.notUsed1 = False           # C 1: Do 3 -
        self.notUsed2 = False           # C 1: Do 4 -
        self.notUsed3 = False           # C 1: Do 5 -
        self.notUsed4 = False           # C 1: Do 6 -
        self.notUsed5 = False           # C 1: Do 7 -
        self.notUsed6 = False           # C 1: Do 8 -
        self.notUsed7 = False           # C 1: Do 9 -
        self.notUsed8 = False           # C 1: Do 10-
        self.notUsed9 = False           # C 1: Do 11-
        self.notUsed10 = False          # C 1: Do 12-
        self.notUsed11 = False          # C 1: Do 13-
        self.notUsed12 = False          # C 1: Do 14-
        self.notUsed13 = False          # C 1: Do 15-
        self.IR_Lamp_1 = False          # C 1: Do 16- Zone 1a
        self.IR_Lamp_2 = False          # C 1: Do 17- Zone 1b
        self.IR_Lamp_3 = False          # C 1: Do 18- Zone 2a
        self.IR_Lamp_4 = False          # C 1: Do 19- Zone 2b
        self.IR_Lamp_5 = False          # C 1: Do 20- Zone 3a
        self.IR_Lamp_6 = False          # C 1: Do 21- Zone 3b
        self.IR_Lamp_7 = False          # C 1: Do 22- Zone 4a
        self.IR_Lamp_8 = False          # C 1: Do 23- Zone 4b
        self.IR_Lamp_9 = False          # C 1: Do 24- Zone 5a
        self.IR_Lamp_10 = False         # C 1: Do 25- Zone 5b
        self.IR_Lamp_11 = False         # C 1: Do 26- Zone 6a
        self.IR_Lamp_12 = False         # C 1: Do 27- Zone 6b
        self.IR_Lamp_13 = False         # C 1: Do 28- Zone 7a
        self.IR_Lamp_14 = False         # C 1: Do 29- Zone 7b
        self.IR_Lamp_15 = False         # C 1: Do 30- Zone 8a
        self.IR_Lamp_16 = False         # C 1: Do 31- Zone 8b
        self.Heater_1 = False           # C 2: Do 0 - Platen Heaters 1 & 2 - Zone 9
        self.Heater_2 = False           # C 2: Do 1 - Platen Heaters 3 & 4 - Zone 9
        self.Heater_3 = False           # C 2: Do 2 - Platen Heaters 5 & 6 - Zone 9
        self.Heater_4 = False           # C 2: Do 3 - Platen Heaters 7 & 8 - Zone 9
        self.Heater_5 = False           # C 2: Do 4 - Platen Heaters 9 & 10 - Zone 9
        self.Heater_6 = False           # C 2: Do 5 - Platen Heaters 11 & 12 - Zone 9
        self.Heater_7 = False           # C 2: Do 6 -
        self.Heater_8 = False           # C 2: Do 7 -
        self.Heater_9 = False           # C 2: Do 8 -
        self.Heater_10 = False          # C 2: Do 9 -
        self.Heater_11 = False          # C 2: Do 10-
        self.Heater_12 = False          # C 2: Do 11-
        self.Heater_13 = False          # C 2: Do 12-
        self.Heater_14 = False          # C 2: Do 13-
        self.Heater_15 = False          # C 2: Do 14-
        self.Heater_16 = False          # C 2: Do 15-
        self.Heater_17 = False          # C 2: Do 16-
        self.Heater_18 = False          # C 2: Do 17-
        self.Heater_19 = False          # C 2: Do 18-
        self.Heater_20 = False          # C 2: Do 19-
        self.Heater_21 = False          # C 2: Do 20-
        self.MCC_Power = False          # C 2: Do 21-
        self.MCC2_Power = False         # C 2: Do 22-
        self.RoughP_GateValve = False   # C 2: Do 23-
        self.RoughP_Start = False       # C 2: Do 24-
        self.CryoP_GateValve = False    # C 2: Do 25-
        self.RoughP_PurgeGass = False   # C 2: Do 26-
        self.LN2_S_Sol = False          # C 2: Do 27-
        self.LN2_P_Sol = False          # C 2: Do 28-
        self.CryoP_PwrRelay1 = False    # C 2: Do 29-
        self.CryoP_PwrRelay2 = False    # C 2: Do 30-
        self.RoughP_PwrRelay = False    # C 2: Do 31-

    def updatePin(self, CardNum, pinNum, setBit):  # Todo Delete this method when not used in engr_ interface
        # Do not use this funciton in the real server
        # this is a hack for the engr_interface
        pinNum = 31 & int(pinNum - 1)
        if CardNum == 2:
            if (pinNum >> 3) == 3:
                key = "C2 B3"
                val = self.c2_b3
            elif (pinNum >> 3) == 2:
                key = "C2 B2"
                val = self.c2_b2
            elif (pinNum >> 3) == 1:
                key = "C2 B1"
                val = self.c2_b1
            else:
                key = "C2 B0"
                val = self.c2_b0
        else:
            if (pinNum >> 3) == 3:
                key = "C1 B3"
                val = self.c1_b3
            elif (pinNum >> 3) == 2:
                key = "C1 B2"
                val = self.c1_b2
            elif (pinNum >> 3) == 1:
                key = "C1 B1"
                val = self.c1_b1
            else:
                key = "C1 B0"
                val = self.c1_b0
        mask = 0x01 << (7 & pinNum)
        if setBit:
            val |= mask
        else:  # clearBit
            val &= ~mask
        self.update({key: val})
        # Todo Delete this method when not used in engr_ interface

    def update(self, d):
        self.__updateLock.acquire()
        if 'C1 B0' in d:
            self.c1_b0 = d['C1 B0']
            self.LN2_P_EN = ((self.c1_b0 & 0x01) > 0)  # C 1: Do 0
            self.LN2_S_EN = ((self.c1_b0 & 0x02) > 0)  # C 1: Do 1
            self.LN2_Sol_EN = ((self.c1_b0 & 0x04) > 0)  # C 1: Do 2
            self.notUsed1 = ((self.c1_b0 & 0x08) > 0)  # C 1: Do 3
            self.notUsed2 = ((self.c1_b0 & 0x10) > 0)  # C 1: Do 4
            self.notUsed3 = ((self.c1_b0 & 0x20) > 0)  # C 1: Do 5
            self.notUsed4 = ((self.c1_b0 & 0x40) > 0)  # C 1: Do 6
            self.notUsed5 = ((self.c1_b0 & 0x80) > 0)  # C 1: Do 7
        if 'LN2_P_EN' in d:
            self.LN2_P_EN = d['LN2_P_EN']
            if self.LN2_P_EN:
                self.c1_b0 |= 0x01        # C 1: Do 0
            else:
                self.c1_b0 &= ~0x01
        if 'LN2_S_EN' in d:
            self.LN2_S_EN = d['LN2_S_EN']
            if self.LN2_S_EN:
                self.c1_b0 |= 0x02        # C 1: Do 1
            else:
                self.c1_b0 &= ~0x02
        if 'LN2_Sol_EN' in d:
            self.LN2_Sol_EN = d['LN2_Sol_EN']
            if self.LN2_Sol_EN:
                self.c1_b0 |= 0x04        # C 1: Do 2
            else:
                self.c1_b0 &= ~0x04
        if 'notUsed1' in d:
            self.notUsed1 = d['notUsed1']
            if self.notUsed1:
                self.c1_b0 |= 0x08        # C 1: Do 3
            else:
                self.c1_b0 &= ~0x08
        if 'notUsed2' in d:
            self.notUsed2 = d['notUsed2']
            if self.notUsed2:
                self.c1_b0 |= 0x10        # C 1: Do 4
            else:
                self.c1_b0 &= ~0x10
        if 'notUsed3' in d:
            self.notUsed3 = d['notUsed3']
            if self.notUsed3:
                self.c1_b0 |= 0x20        # C 1: Do 5
            else:
                self.c1_b0 &= ~0x20
        if 'notUsed4' in d:
            self.notUsed4 = d['notUsed4']
            if self.notUsed4:
                self.c1_b0 |= 0x40        # C 1: Do 6
            else:
                self.c1_b0 &= ~0x40
        if 'notUsed5' in d:
            self.notUsed5 = d['notUsed5']
            if self.notUsed5:
                self.c1_b0 |= 0x80        # C 1: Do 7
            else:
                self.c1_b0 &= ~0x80

        if 'C1 B1' in d:
            self.c1_b1 = d['C1 B1']
            self.notUsed6 = ((self.c1_b1 & 0x01) > 0)  # C 1: Do 8
            self.notUsed7 = ((self.c1_b1 & 0x02) > 0)  # C 1: Do 9
            self.notUsed8 = ((self.c1_b1 & 0x04) > 0)  # C 1: Do 10
            self.notUsed9 = ((self.c1_b1 & 0x08) > 0)  # C 1: Do 11
            self.notUsed10 = ((self.c1_b1 & 0x10) > 0)  # C 1: Do 12
            self.notUsed11 = ((self.c1_b1 & 0x20) > 0)  # C 1: Do 13
            self.notUsed12 = ((self.c1_b1 & 0x40) > 0)  # C 1: Do 14
            self.notUsed13 = ((self.c1_b1 & 0x80) > 0)  # C 1: Do 15
        if 'notUsed6' in d:
            self.notUsed6 = d['notUsed6']
            if self.notUsed6:
                self.c1_b1 |= 0x01        # C 1: Do 8
            else:
                self.c1_b1 &= ~0x01
        if 'notUsed7' in d:
            self.notUsed7 = d['notUsed7']
            if self.notUsed7:
                self.c1_b1 |= 0x02        # C 1: Do 9
            else:
                self.c1_b1 &= ~0x02
        if 'notUsed8' in d:
            self.notUsed8 = d['notUsed8']
            if self.notUsed8:
                self.c1_b1 |= 0x04        # C 1: Do 10
            else:
                self.c1_b1 &= ~0x04
        if 'notUsed9' in d:
            self.notUsed9 = d['notUsed9']
            if self.notUsed9:
                self.c1_b1 |= 0x08        # C 1: Do 11
            else:
                self.c1_b1 &= ~0x08
        if 'notUsed10' in d:
            self.notUsed10 = d['notUsed10']
            if self.notUsed10:
                self.c1_b1 |= 0x10        # C 1: Do 12
            else:
                self.c1_b1 &= ~0x10
        if 'notUsed11' in d:
            self.notUsed11 = d['notUsed11']
            if self.notUsed11:
                self.c1_b1 |= 0x20        # C 1: Do 13
            else:
                self.c1_b1 &= ~0x20
        if 'notUsed12' in d:
            self.notUsed12 = d['notUsed12']
            if self.notUsed12:
                self.c1_b1 |= 0x40        # C 1: Do 14
            else:
                self.c1_b1 &= ~0x40
        if 'notUsed13' in d:
            self.notUsed13 = d['notUsed13']
            if self.notUsed13:
                self.c1_b1 |= 0x80        # C 1: Do 15
            else:
                self.c1_b1 &= ~0x80

        if 'C1 B2' in d:
            self.c1_b2 = d['C1 B2']
            self.IR_Lamp_1 = ((self.c1_b2 & 0x01) > 0)  # C 1: Do 16
            self.IR_Lamp_2 = ((self.c1_b2 & 0x02) > 0)  # C 1: Do 17
            self.IR_Lamp_3 = ((self.c1_b2 & 0x04) > 0)  # C 1: Do 18
            self.IR_Lamp_4 = ((self.c1_b2 & 0x08) > 0)  # C 1: Do 19
            self.IR_Lamp_5 = ((self.c1_b2 & 0x10) > 0)  # C 1: Do 20
            self.IR_Lamp_6 = ((self.c1_b2 & 0x20) > 0)  # C 1: Do 21
            self.IR_Lamp_7 = ((self.c1_b2 & 0x40) > 0)  # C 1: Do 22
            self.IR_Lamp_8 = ((self.c1_b2 & 0x80) > 0)  # C 1: Do 23
        if 'IR_Lamp_1' in d:
            self.IR_Lamp_1 = d['IR_Lamp_1']
            if self.IR_Lamp_1:
                self.c1_b2 |= 0x01        # C 1: Do 16
            else:
                self.c1_b2 &= ~0x01
        if 'IR_Lamp_2' in d:
            self.IR_Lamp_2 = d['IR_Lamp_2']
            if self.IR_Lamp_2:
                self.c1_b2 |= 0x02        # C 1: Do 17
            else:
                self.c1_b2 &= ~0x02
        if 'IR_Lamp_3' in d:
            self.IR_Lamp_3 = d['IR_Lamp_3']
            if self.IR_Lamp_3:
                self.c1_b2 |= 0x04        # C 1: Do 18
            else:
                self.c1_b2 &= ~0x04
        if 'IR_Lamp_4' in d:
            self.IR_Lamp_4 = d['IR_Lamp_4']
            if self.IR_Lamp_4:
                self.c1_b2 |= 0x08        # C 1: Do 19
            else:
                self.c1_b2 &= ~0x08
        if 'IR_Lamp_5' in d:
            self.IR_Lamp_5 = d['IR_Lamp_5']
            if self.IR_Lamp_5:
                self.c1_b2 |= 0x10        # C 1: Do 20
            else:
                self.c1_b2 &= ~0x10
        if 'IR_Lamp_6' in d:
            self.IR_Lamp_6 = d['IR_Lamp_6']
            if self.IR_Lamp_6:
                self.c1_b2 |= 0x20        # C 1: Do 21
            else:
                self.c1_b2 &= ~0x20
        if 'IR_Lamp_7' in d:
            self.IR_Lamp_7 = d['IR_Lamp_7']
            if self.IR_Lamp_7:
                self.c1_b2 |= 0x40        # C 1: Do 22
            else:
                self.c1_b2 &= ~0x40
        if 'IR_Lamp_8' in d:
            self.IR_Lamp_8 = d['IR_Lamp_8']
            if self.IR_Lamp_8:
                self.c1_b2 |= 0x80        # C 1: Do 23
            else:
                self.c1_b2 &= ~0x80

        if 'C1 B3' in d:
            self.c1_b3 = d['C1 B3']
            self.IR_Lamp_9 = ((self.c1_b3 & 0x01) > 0)  # C 1: Do 24
            self.IR_Lamp_10 = ((self.c1_b3 & 0x02) > 0)  # C 1: Do 25
            self.IR_Lamp_11 = ((self.c1_b3 & 0x04) > 0)  # C 1: Do 26
            self.IR_Lamp_12 = ((self.c1_b3 & 0x08) > 0)  # C 1: Do 27
            self.IR_Lamp_13 = ((self.c1_b3 & 0x10) > 0)  # C 1: Do 28
            self.IR_Lamp_14 = ((self.c1_b3 & 0x20) > 0)  # C 1: Do 29
            self.IR_Lamp_15 = ((self.c1_b3 & 0x40) > 0)  # C 1: Do 30
            self.IR_Lamp_16 = ((self.c1_b3 & 0x80) > 0)  # C 1: Do 31
        if 'IR_Lamp_9' in d:
            self.IR_Lamp_9 = d['IR_Lamp_9']
            if self.IR_Lamp_9:
                self.c1_b3 |= 0x01        # C 1: Do 24
            else:
                self.c1_b3 &= ~0x01
        if 'IR_Lamp_10' in d:
            self.IR_Lamp_10 = d['IR_Lamp_10']
            if self.IR_Lamp_10:
                self.c1_b3 |= 0x02        # C 1: Do 25
            else:
                self.c1_b3 &= ~0x02
        if 'IR_Lamp_11' in d:
            self.IR_Lamp_11 = d['IR_Lamp_11']
            if self.IR_Lamp_11:
                self.c1_b3 |= 0x04        # C 1: Do 26
            else:
                self.c1_b3 &= ~0x04
        if 'IR_Lamp_12' in d:
            self.IR_Lamp_12 = d['IR_Lamp_12']
            if self.IR_Lamp_12:
                self.c1_b3 |= 0x08        # C 1: Do 27
            else:
                self.c1_b3 &= ~0x08
        if 'IR_Lamp_13' in d:
            self.IR_Lamp_13 = d['IR_Lamp_13']
            if self.IR_Lamp_13:
                self.c1_b3 |= 0x10        # C 1: Do 28
            else:
                self.c1_b3 &= ~0x10
        if 'IR_Lamp_14' in d:
            self.IR_Lamp_14 = d['IR_Lamp_14']
            if self.IR_Lamp_14:
                self.c1_b3 |= 0x20        # C 1: Do 29
            else:
                self.c1_b3 &= ~0x20
        if 'IR_Lamp_15' in d:
            self.IR_Lamp_15 = d['IR_Lamp_15']
            if self.IR_Lamp_15:
                self.c1_b3 |= 0x40        # C 1: Do 30
            else:
                self.c1_b3 &= ~0x40
        if 'IR_Lamp_16' in d:
            self.IR_Lamp_16 = d['IR_Lamp_16']
            if self.IR_Lamp_16:
                self.c1_b3 |= 0x80        # C 1: Do 31
            else:
                self.c1_b3 &= ~0x80

        if 'C2 B0' in d:
            self.c2_b0 = d['C2 B0']
            self.Heater_1 = ((self.c2_b0 & 0x01) > 0)  # C 2: Do 0
            self.Heater_2 = ((self.c2_b0 & 0x02) > 0)  # C 2: Do 1
            self.Heater_3 = ((self.c2_b0 & 0x04) > 0)  # C 2: Do 2
            self.Heater_4 = ((self.c2_b0 & 0x08) > 0)  # C 2: Do 3
            self.Heater_5 = ((self.c2_b0 & 0x10) > 0)  # C 2: Do 4
            self.Heater_6 = ((self.c2_b0 & 0x20) > 0)  # C 2: Do 5
            self.Heater_7 = ((self.c2_b0 & 0x40) > 0)  # C 2: Do 6
            self.Heater_8 = ((self.c2_b0 & 0x80) > 0)  # C 2: Do 7
        if 'Heater_1' in d:
            self.Heater_1 = d['Heater_1']
            if self.Heater_1:
                self.c2_b0 |= 0x01        # C 2: Do 0
            else:
                self.c2_b0 &= ~0x01
        if 'Heater_2' in d:
            self.Heater_2 = d['Heater_2']
            if self.Heater_2:
                self.c2_b0 |= 0x02        # C 2: Do 1
            else:
                self.c2_b0 &= ~0x02
        if 'Heater_3' in d:
            self.Heater_3 = d['Heater_3']
            if self.Heater_3:
                self.c2_b0 |= 0x04        # C 2: Do 2
            else:
                self.c2_b0 &= ~0x04
        if 'Heater_4' in d:
            self.Heater_4 = d['Heater_4']
            if self.Heater_4:
                self.c2_b0 |= 0x08        # C 2: Do 3
            else:
                self.c2_b0 &= ~0x08
        if 'Heater_5' in d:
            self.Heater_5 = d['Heater_5']
            if self.Heater_5:
                self.c2_b0 |= 0x10        # C 2: Do 4
            else:
                self.c2_b0 &= ~0x10
        if 'Heater_6' in d:
            self.Heater_6 = d['Heater_6']
            if self.Heater_6:
                self.c2_b0 |= 0x20        # C 2: Do 5
            else:
                self.c2_b0 &= ~0x20
        if 'Heater_7' in d:
            self.Heater_7 = d['Heater_7']
            if self.Heater_7:
                self.c2_b0 |= 0x40        # C 2: Do 6
            else:
                self.c2_b0 &= ~0x40
        if 'Heater_8' in d:
            self.Heater_8 = d['Heater_8']
            if self.Heater_8:
                self.c2_b0 |= 0x80        # C 2: Do 7
            else:
                self.c2_b0 &= ~0x80

        if 'C2 B1' in d:
            self.c2_b1 = d['C2 B1']
            self.Heater_9 = ((self.c2_b1 & 0x01) > 0)  # C 2: Do 8
            self.Heater_10 = ((self.c2_b1 & 0x02) > 0)  # C 2: Do 9
            self.Heater_11 = ((self.c2_b1 & 0x04) > 0)  # C 2: Do 10
            self.Heater_12 = ((self.c2_b1 & 0x08) > 0)  # C 2: Do 11
            self.Heater_13 = ((self.c2_b1 & 0x10) > 0)  # C 2: Do 12
            self.Heater_14 = ((self.c2_b1 & 0x20) > 0)  # C 2: Do 13
            self.Heater_15 = ((self.c2_b1 & 0x40) > 0)  # C 2: Do 14
            self.Heater_16 = ((self.c2_b1 & 0x80) > 0)  # C 2: Do 15
        if 'Heater_9' in d:
            self.Heater_9 = d['Heater_9']
            if self.Heater_9:
                self.c2_b1 |= 0x01        # C 2: Do 8
            else:
                self.c2_b1 &= ~0x01
        if 'Heater_10' in d:
            self.Heater_10 = d['Heater_10']
            if self.Heater_10:
                self.c2_b1 |= 0x02        # C 2: Do 9
            else:
                self.c2_b1 &= ~0x02
        if 'Heater_11' in d:
            self.Heater_11 = d['Heater_11']
            if self.Heater_11:
                self.c2_b1 |= 0x04        # C 2: Do 10
            else:
                self.c2_b1 &= ~0x04
        if 'Heater_12' in d:
            self.Heater_12 = d['Heater_12']
            if self.Heater_12:
                self.c2_b1 |= 0x08        # C 2: Do 11
            else:
                self.c2_b1 &= ~0x08
        if 'Heater_13' in d:
            self.Heater_13 = d['Heater_13']
            if self.Heater_13:
                self.c2_b1 |= 0x10        # C 2: Do 12
            else:
                self.c2_b1 &= ~0x10
        if 'Heater_14' in d:
            self.Heater_14 = d['Heater_14']
            if self.Heater_14:
                self.c2_b1 |= 0x20        # C 2: Do 13
            else:
                self.c2_b1 &= ~0x20
        if 'Heater_15' in d:
            self.Heater_15 = d['Heater_15']
            if self.Heater_15:
                self.c2_b1 |= 0x40        # C 2: Do 14
            else:
                self.c2_b1 &= ~0x40
        if 'Heater_16' in d:
            self.Heater_16 = d['Heater_16']
            if self.Heater_16:
                self.c2_b1 |= 0x80        # C 2: Do 15
            else:
                self.c2_b1 &= ~0x80

        if 'C2 B2' in d:
            self.c2_b2 = d['C2 B2']
            self.Heater_17 = ((self.c2_b2 & 0x01) > 0)  # C 2: Do 16
            self.Heater_18 = ((self.c2_b2 & 0x02) > 0)  # C 2: Do 17
            self.Heater_19 = ((self.c2_b2 & 0x04) > 0)  # C 2: Do 18
            self.Heater_20 = ((self.c2_b2 & 0x08) > 0)  # C 2: Do 19
            self.Heater_21 = ((self.c2_b2 & 0x10) > 0)  # C 2: Do 20
            self.MCC_Power = ((self.c2_b2 & 0x20) > 0)  # C 2: Do 21
            self.MCC2_Power = ((self.c2_b2 & 0x40) > 0)  # C 2: Do 22
            self.RoughP_GateValve = ((self.c2_b2 & 0x80) > 0)  # C 2: Do 23
        if 'Heater_17' in d:
            self.Heater_17 = d['Heater_17']
            if self.Heater_17:
                self.c2_b2 |= 0x01        # C 2: Do 16
            else:
                self.c2_b2 &= ~0x01
        if 'Heater_18' in d:
            self.Heater_18 = d['Heater_18']
            if self.Heater_18:
                self.c2_b2 |= 0x02        # C 2: Do 17
            else:
                self.c2_b2 &= ~0x02
        if 'Heater_19' in d:
            self.Heater_19 = d['Heater_19']
            if self.Heater_19:
                self.c2_b2 |= 0x04        # C 2: Do 18
            else:
                self.c2_b2 &= ~0x04
        if 'Heater_20' in d:
            self.Heater_20 = d['Heater_20']
            if self.Heater_20:
                self.c2_b2 |= 0x08        # C 2: Do 19
            else:
                self.c2_b2 &= ~0x08
        if 'Heater_21' in d:
            self.Heater_21 = d['Heater_21']
            if self.Heater_21:
                self.c2_b2 |= 0x10        # C 2: Do 20
            else:
                self.c2_b2 &= ~0x10
        if 'MCC_Power' in d:
            self.MCC_Power = d['MCC_Power']
            if self.MCC_Power:
                self.c2_b2 |= 0x20        # C 2: Do 21
            else:
                self.c2_b2 &= ~0x20
        if 'MCC2_Power' in d:
            self.MCC2_Power = d['MCC2_Power']
            if self.MCC2_Power:
                self.c2_b2 |= 0x40        # C 2: Do 22
            else:
                self.c2_b2 &= ~0x40
        if 'RoughP_GateValve' in d:
            self.RoughP_GateValve = d['RoughP_GateValve']
            if self.RoughP_GateValve:
                self.c2_b2 |= 0x80        # C 2: Do 23
            else:
                self.c2_b2 &= ~0x80

        if 'C2 B3' in d:
            self.c2_b3 = d['C2 B3']
            self.RoughP_Start = ((self.c2_b3 & 0x01) > 0)  # C 2: Do 24
            self.CryoP_GateValve = ((self.c2_b3 & 0x02) > 0)  # C 2: Do 25
            self.RoughP_PurgeGass = ((self.c2_b3 & 0x04) > 0)  # C 2: Do 26
            self.LN2_S_Sol = ((self.c2_b3 & 0x08) > 0)  # C 2: Do 27
            self.LN2_P_Sol = ((self.c2_b3 & 0x10) > 0)  # C 2: Do 28
            self.CryoP1_PwrRelay = ((self.c2_b3 & 0x20) > 0)  # C 2: Do 29
            self.CryoP2_PwrRelay = ((self.c2_b3 & 0x40) > 0)  # C 2: Do 30
            self.RoughP_PwrRelay = ((self.c2_b3 & 0x80) > 0)  # C 2: Do 31
        if 'RoughP_Start' in d:
            self.RoughP_Start = d['RoughP_Start']
            if self.RoughP_Start:
                self.c2_b3 |= 0x01        # C 2: Do 24
            else:
                self.c2_b3 &= ~0x01
        if 'CryoP_GateValve' in d:
            self.CryoP_GateValve = d['CryoP_GateValve']
            if self.CryoP_GateValve:
                self.c2_b3 |= 0x02        # C 2: Do 25
            else:
                self.c2_b3 &= ~0x02
        if 'RoughP_PurgeGass' in d:
            self.RoughP_PurgeGass = d['RoughP_PurgeGass']
            if self.RoughP_PurgeGass:
                self.c2_b3 |= 0x04        # C 2: Do 26
            else:
                self.c2_b3 &= ~0x04
        if 'LN2_S_Sol' in d:
            self.LN2_S_Sol = d['LN2_S_Sol']
            if self.LN2_S_Sol:
                self.c2_b3 |= 0x08        # C 2: Do 27
            else:
                self.c2_b3 &= ~0x08
        if 'LN2_P_Sol' in d:
            self.LN2_P_Sol = d['LN2_P_Sol']
            if self.LN2_P_Sol:
                self.c2_b3 |= 0x10        # C 2: Do 28
            else:
                self.c2_b3 &= ~0x10
        if 'CryoP1_PwrRelay' in d:
            self.CryoP1_PwrRelay = d['CryoP1_PwrRelay']
            if self.CryoP1_PwrRelay:
                self.c2_b3 |= 0x20        # C 2: Do 29
            else:
                self.c2_b3 &= ~0x20
        if 'CryoP2_PwrRelay' in d:
            self.CryoP2_PwrRelay = d['CryoP2_PwrRelay']
            if self.CryoP2_PwrRelay:
                self.c2_b3 |= 0x40        # C 2: Do 30
            else:
                self.c2_b3 &= ~0x40
        if 'RoughP_PwrRelay' in d:
            self.RoughP_PwrRelay = d['RoughP_PwrRelay']
            if self.RoughP_PwrRelay:
                self.c2_b3 |= 0x80        # C 2: Do 31
            else:
                self.c2_b3 &= ~0x80
        self.__updateLock.release()

    def getJson(self):
        message = []
        message.append('{"LN2_P_EN":%s,' % self.LN2_P_EN)
        message.append('"LN2_S_EN":%s,' % self.LN2_S_EN)
        message.append('"LN2_Sol_EN":%s,' % self.LN2_Sol_EN)
        #message.append('"notUsed1":%s,' % self.notUsed1) uncomment when this is used
        message.append('"IR_Lamp_1":%s,' % self.IR_Lamp_1)
        message.append('"IR_Lamp_2":%s,' % self.IR_Lamp_2)
        message.append('"IR_Lamp_3":%s,' % self.IR_Lamp_3)
        message.append('"IR_Lamp_4":%s,' % self.IR_Lamp_4)
        message.append('"IR_Lamp_5":%s,' % self.IR_Lamp_5)
        message.append('"IR_Lamp_6":%s,' % self.IR_Lamp_6)
        message.append('"IR_Lamp_7":%s,' % self.IR_Lamp_7)
        message.append('"IR_Lamp_8":%s,' % self.IR_Lamp_8)
        message.append('"IR_Lamp_9":%s,' % self.IR_Lamp_9)
        message.append('"IR_Lamp_10":%s,' % self.IR_Lamp_10)
        message.append('"IR_Lamp_11":%s,' % self.IR_Lamp_11)
        message.append('"IR_Lamp_12":%s,' % self.IR_Lamp_12)
        message.append('"IR_Lamp_13":%s,' % self.IR_Lamp_13)
        message.append('"IR_Lamp_14":%s,' % self.IR_Lamp_14)
        message.append('"IR_Lamp_15":%s,' % self.IR_Lamp_15)
        message.append('"IR_Lamp_16":%s,' % self.IR_Lamp_16)
        message.append('"Heater_1":%s,' % self.Heater_1)
        message.append('"Heater_2":%s,' % self.Heater_2)
        message.append('"Heater_3":%s,' % self.Heater_3)
        message.append('"Heater_4":%s,' % self.Heater_4)
        message.append('"Heater_5":%s,' % self.Heater_5)
        message.append('"Heater_6":%s,' % self.Heater_6)
        message.append('"Heater_7":%s,' % self.Heater_7)
        message.append('"Heater_8":%s,' % self.Heater_8)
        message.append('"Heater_9":%s,' % self.Heater_9)
        message.append('"Heater_10":%s,' % self.Heater_10)
        message.append('"Heater_11":%s,' % self.Heater_11)
        message.append('"Heater_12":%s,' % self.Heater_12)
        message.append('"Heater_13":%s,' % self.Heater_13)
        message.append('"Heater_14":%s,' % self.Heater_14)
        message.append('"Heater_15":%s,' % self.Heater_15)
        message.append('"Heater_16":%s,' % self.Heater_16)
        message.append('"Heater_17":%s,' % self.Heater_17)
        message.append('"Heater_18":%s,' % self.Heater_18)
        message.append('"Heater_19":%s,' % self.Heater_19)
        message.append('"Heater_20":%s,' % self.Heater_20)
        message.append('"Heater_21":%s,' % self.Heater_21)
        message.append('"MCC_Power":%s,' % self.MCC_Power)
        message.append('"MCC2_Power":%s,' % self.MCC2_Power)
        message.append('"RoughP_GateValve":%s,' % self.RoughP_GateValve)
        message.append('"RoughP_Start":%s,' % self.RoughP_Start)
        message.append('"CryoP_GateValve":%s,' % self.CryoP_GateValve)
        message.append('"RoughP_PurgeGass":%s,' % self.RoughP_PurgeGass)
        message.append('"LN2_S_Sol":%s,' % self.LN2_S_Sol)
        message.append('"LN2_P_Sol":%s,' % self.LN2_P_Sol)
        message.append('"CryoP_PwrRelay1":%s,' % self.CryoP_PwrRelay1)
        message.append('"CryoP_PwrRelay2":%s,' % self.CryoP_PwrRelay2)
        message.append('"RoughP_PwrRelay":%s}' %self.RoughP_PwrRelay)
        return ''.join(message)
