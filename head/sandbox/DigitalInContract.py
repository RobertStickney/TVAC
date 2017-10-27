import threading
import json


class DigitalInContract:    

    __lock = threading.RLock()

    def __init__(self):
        self.pgRoughPumpRelay1 = False    # C 1: Di 0 - Roughing Pump Pressure Gauge Relay 1
        self.pgRoughPumpRelay2 = False    # C 1: Di 1 - Roughing Pump Pressure Gauge Relay 2
        self.pgCryoPumpRelay1 = False     # C 1: Di 2 - Cryo-pump Pressure Gauge Relay 1
        self.pgCryoPumpRelay2 = False     # C 1: Di 3 - Cryo-pump Pressure Gauge Relay 2
        self.pgChamberRelay1 = False      # C 1: Di 4 - Chamber Pressure Gauge Relay 1
        self.pgChamberRelay2 = False      # C 1: Di 5 - Chamber Pressure Gauge Relay 2
        self.LN2_P_Sol_Open_NC = False    # C 1: Di 6 -
        self.LN2_P_Sol_Open_O = False     # C 1: Di 7 -
        self.LN2_P_Sol_Closed_NC = False  # C 1: Di 8 -
        self.LN2_P_Sol_Closed_O = False   # C 1: Di 9 -
        self.LN2_S_Sol_Open_NC = False    # C 1: Di 10-
        self.LN2_S_Sol_Open_O = False     # C 1: Di 11-
        self.LN2_S_Sol_Closed_NC = False  # C 1: Di 12-
        self.LN2_S_Sol_Closed_O = False   # C 1: Di 13-
        self.CryoP_GV_Open_NC = False     # C 1: Di 14-
        self.CryoP_GV_Open_O = False      # C 1: Di 15-
        self.CryoP_GV_Closed_NC = False   # C 1: Di 16-
        self.CryoP_GV_Closed_O = False    # C 1: Di 17-
        self.RoughP_GV_Open = False       # C 1: Di 18-
        self.RoughP_GV_Closed = False     # C 1: Di 19-
        self.RoughP_Pwr_NC = False        # C 1: Di 20-
        self.RoughP_Pwr_O = False         # C 1: Di 21-
        self.RoughP_On_NC = False         # C 1: Di 22-
        self.RoughP_On_O = False          # C 1: Di 23-
        self.notUsed1 = False             # C 1: Di 24- Unassigned channel 24
        self.notUsed2 = False             # C 1: Di 25- Unassigned channel 25
        self.notUsed3 = False             # C 1: Di 26- Unassigned channel 26
        self.notUsed4 = False             # C 1: Di 27- Unassigned channel 27
        self.notUsed5 = False             # C 1: Di 28- Unassigned channel 28
        self.notUsed6 = False             # C 1: Di 29- Unassigned channel 29
        self.LN2AirOK = False             # C 1: Di 30- 100 psi Air supply connected to the LN2 supply valves
        self.AirOK = False                # C 1: Di 31- 100 psi Air supply connected to the TVAC
        self.t20 = False                  # C 2: Di 0 -
        self.t21 = False                  # C 2: Di 1 -
        self.t22 = False                  # C 2: Di 2 -
        self.t23 = False                  # C 2: Di 3 -
        self.t24 = False                  # C 2: Di 4 -
        self.t25 = False                  # C 2: Di 5 -
        self.t26 = False                  # C 2: Di 6 -
        self.t27 = False                  # C 2: Di 7 -
        self.t28 = False                  # C 2: Di 8 -
        self.t29 = False                  # C 2: Di 9 -
        self.t30 = False                  # C 2: Di 10-
        self.t31 = False                  # C 2: Di 11-
        self.t32 = False                  # C 2: Di 12-
        self.t33 = False                  # C 2: Di 13-
        self.t34 = False                  # C 2: Di 14-
        self.t35 = False                  # C 2: Di 15-
        self.t36 = False                  # C 2: Di 16-
        self.t37 = False                  # C 2: Di 17-
        self.t38 = False                  # C 2: Di 18-
        self.t39 = False                  # C 2: Di 19-
        self.t40 = False                  # C 2: Di 20-
        self.t41 = False                  # C 2: Di 21-
        self.t42 = False                  # C 2: Di 22-
        self.t43 = False                  # C 2: Di 23-
        self.t44 = False                  # C 2: Di 24-
        self.t45 = False                  # C 2: Di 25-
        self.notUsed7 = False             # C 2: Di 26-
        self.notUsed8 = False             # C 2: Di 27-
        self.notUsed9 = False             # C 2: Di 28-
        self.notUsed10 = False            # C 2: Di 29-
        self.notUsed11 = False            # C 2: Di 30-
        self.LN2en = False                # C 2: Di 31- LN2 flow is enabled

    def update(self, d):
        self.__lock.acquire()
        if 'C1 B0' in d:
            self.pgRoughPumpRelay1 = ((d['C1 B0'] & 0x01) > 0)  # C 1: Di 1
            self.pgRoughPumpRelay2 = ((d['C1 B0'] & 0x02) > 0)  # C 1: Di 1
            self.pgCryoPumpRelay1 = ((d['C1 B0'] & 0x04) > 0)  # C 1: Di 2
            self.pgCryoPumpRelay2 = ((d['C1 B0'] & 0x08) > 0)  # C 1: Di 3
            self.pgChamberRelay1 = ((d['C1 B0'] & 0x10) > 0)  # C 1: Di 4
            self.pgChamberRelay2 = ((d['C1 B0'] & 0x20) > 0)  # C 1: Di 5
            self.LN2_P_Sol_Open_NC = ((d['C1 B0'] & 0x40) > 0)  # C 1: Di 6
            self.LN2_P_Sol_Open_O = ((d['C1 B0'] & 0x80) > 0)  # C 1: Di 7
        if 'C1 B1' in d:
            self.LN2_P_Sol_Closed_NC = ((d['C1 B1'] & 0x01) > 0)  # C 1: Di 8
            self.LN2_P_Sol_Closed_O = ((d['C1 B1'] & 0x02) > 0)  # C 1: Di 9
            self.LN2_S_Sol_Open_NC = ((d['C1 B1'] & 0x04) > 0)  # C 1: Di 10
            self.LN2_S_Sol_Open_O = ((d['C1 B1'] & 0x08) > 0)  # C 1: Di 11
            self.LN2_S_Sol_Closed_NC = ((d['C1 B1'] & 0x10) > 0)  # C 1: Di 12
            self.LN2_S_Sol_Closed_O = ((d['C1 B1'] & 0x20) > 0)  # C 1: Di 13
            self.CryoP_GV_Open_NC = ((d['C1 B1'] & 0x40) > 0)  # C 1: Di 14
            self.CryoP_GV_Open_O = ((d['C1 B1'] & 0x80) > 0)  # C 1: Di 15
        if 'C1 B2' in d:
            self.CryoP_GV_Closed_NC = ((d['C1 B2'] & 0x01) > 0)  # C 1: Di 16
            self.CryoP_GV_Closed_O = ((d['C1 B2'] & 0x02) > 0)  # C 1: Di 17
            self.RoughP_GV_Open = ((d['C1 B2'] & 0x04) > 0)  # C 1: Di 18
            self.RoughP_GV_Closed = ((d['C1 B2'] & 0x08) > 0)  # C 1: Di 19
            self.RoughP_Pwr_NC = ((d['C1 B2'] & 0x10) > 0)  # C 1: Di 20
            self.RoughP_Pwr_O = ((d['C1 B2'] & 0x20) > 0)  # C 1: Di 21
            self.RoughP_On_NC = ((d['C1 B2'] & 0x40) > 0)  # C 1: Di 22
            self.RoughP_On_O = ((d['C1 B2'] & 0x80) > 0)  # C 1: Di 23
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
            self.notUsed7 = ((d['C2 B3'] & 0x04) > 0)  # C 2: Di 26
            self.notUsed8 = ((d['C2 B3'] & 0x08) > 0)  # C 2: Di 27
            self.notUsed9 = ((d['C2 B3'] & 0x10) > 0)  # C 2: Di 28
            self.notUsed10 = ((d['C2 B3'] & 0x20) > 0)  # C 2: Di 29
            self.notUsed11 = ((d['C2 B3'] & 0x40) > 0)  # C 2: Di 30
            self.LN2en = ((d['C2 B3'] & 0x80) > 0)  # C 2: Di 31
        self.__lock.release()

    def getVal(self, name):
        self.__lock.acquire()
        if name == 'pgRoughPumpRelay1':
            val = self.pgRoughPumpRelay1
        elif name == 'pgRoughPumpRelay2':
            val = self.pgRoughPumpRelay2
        elif name == 'pgCryoPumpRelay1':
            val = self.pgCryoPumpRelay1
        elif name == 'pgCryoPumpRelay2':
            val = self.pgCryoPumpRelay2
        elif name == 'pgChamberRelay1':
            val = self.pgChamberRelay1
        elif name == 'pgChamberRelay2':
            val = self.pgChamberRelay2
        elif name == 'LN2_P_Sol_Open_NC':
            val = self.LN2_P_Sol_Open_NC
        elif name == 'LN2_P_Sol_Open_O':
            val = self.LN2_P_Sol_Open_O
        elif name == 'LN2_P_Sol_Closed_NC':
            val = self.LN2_P_Sol_Closed_NC
        elif name == 'LN2_P_Sol_Closed_O':
            val = self.LN2_P_Sol_Closed_O
        elif name == 'LN2_S_Sol_Open_NC':
            val = self.LN2_S_Sol_Open_NC
        elif name == 'LN2_S_Sol_Open_O':
            val = self.LN2_S_Sol_Open_O
        elif name == 'LN2_S_Sol_Closed_NC':
            val = self.LN2_S_Sol_Closed_NC
        elif name == 'LN2_S_Sol_Closed_O':
            val = self.LN2_S_Sol_Closed_O
        elif name == 'CryoP_GV_Open_NC':
            val = self.CryoP_GV_Open_NC
        elif name == 'CryoP_GV_Open_O':
            val = self.CryoP_GV_Open_O
        elif name == 'CryoP_GV_Closed_NC':
            val = self.CryoP_GV_Closed_NC
        elif name == 'CryoP_GV_Closed_O':
            val = self.CryoP_GV_Closed_O
        elif name == 'RoughP_GV_Open':
            val = self.RoughP_GV_Open
        elif name == 'RoughP_GV_Closed':
            val = self.RoughP_GV_Closed
        elif name == 'RoughP_Pwr_NC':
            val = self.RoughP_Pwr_NC
        elif name == 'RoughP_Pwr_O':
            val = self.RoughP_Pwr_O
        elif name == 'RoughP_On_NC':
            val = self.RoughP_On_NC
        elif name == 'RoughP_On_O':
            val = self.RoughP_On_O
        # elif name == 'notUsed1':
        #     val = self.notUsed1
        elif name == 'LN2AirOK':
            val = self.LN2AirOK
        elif name == 'AirOK':
            val = self.AirOK
        # elif name == 'front_door_closed':
        #     val = self.front_door_closed
        # elif name == 'notUsed7':
        #     val = self.notUsed7
        elif name == 'LN2en':
            val = self.LN2en
        else:  # Unknown Value!
            val = None
        self.__lock.release()
        return val

    def getJson(self):
        self.__lock.acquire()
        message = []
        message.append('{"PG-SW-RoughP-Relay 1":%s,' % json.dumps(self.pgRoughPumpRelay1))
        message.append('"PG-SW-RoughP-Relay 2":%s,' % json.dumps(self.pgRoughPumpRelay2))
        message.append('"PG-SW-CryoP-Relay 1":%s,' % json.dumps(self.pgCryoPumpRelay1))
        message.append('"PG-SW-CryoP-Relay 2":%s,' % json.dumps(self.pgCryoPumpRelay2))
        message.append('"PG-SW-Chamber-Relay 1":%s,' % json.dumps(self.pgChamberRelay1))
        message.append('"PG-SW-Chamber-Relay 2":%s,' % json.dumps(self.pgChamberRelay2))
        message.append('"LN2-P-Sol-Open: NC":%s,' % json.dumps(self.LN2_P_Sol_Open_NC))
        message.append('"LN2-P-Sol-Open: O":%s,' % json.dumps(self.LN2_P_Sol_Open_O))
        message.append('"LN2-P-Sol-Closed: NC":%s,' % json.dumps(self.LN2_P_Sol_Closed_NC))
        message.append('"LN2-P-Sol-Closed: O":%s,' % json.dumps(self.LN2_P_Sol_Closed_O))
        message.append('"LN2-S-Sol-Open: NC":%s,' % json.dumps(self.LN2_S_Sol_Open_NC))
        message.append('"LN2-S-Sol-Open: O":%s,' % json.dumps(self.LN2_S_Sol_Open_O))
        message.append('"LN2-S-Sol-Closed: NC":%s,' % json.dumps(self.LN2_S_Sol_Closed_NC))
        message.append('"LN2-S-Sol-Closed: O":%s,' % json.dumps(self.LN2_S_Sol_Closed_O))
        message.append('"CryoP-GV-Open: NC":%s,' % json.dumps(self.CryoP_GV_Open_NC))
        message.append('"CryoP-GV-Open: O":%s,' % json.dumps(self.CryoP_GV_Open_O))
        message.append('"CryoP-GV-Closed: NC":%s,' % json.dumps(self.CryoP_GV_Closed_NC))
        message.append('"CryoP-GV-Closed: O":%s,' % json.dumps(self.CryoP_GV_Closed_O))
        message.append('"RoughP-GV-Open":%s,' % json.dumps(self.RoughP_GV_Open))
        message.append('"RoughP-GV-Closed":%s,' % json.dumps(self.RoughP_GV_Closed))
        message.append('"RoughP-Pwr: NC":%s,' % json.dumps(self.RoughP_Pwr_NC))
        message.append('"RoughP-Pwr: O":%s,' % json.dumps(self.RoughP_Pwr_O))
        message.append('"RoughP-On: NC":%s,' % json.dumps(self.RoughP_On_NC))
        message.append('"RoughP-On: O":%s,' % json.dumps(self.RoughP_On_O))
        #message.append('"notUsed1":%s,' % json.dumps(self.notUsed1)) uncomment when this is used
        message.append('"Air supply LN2 OK":%s,' % json.dumps(self.LN2AirOK))
        message.append('"Air supply OK":%s,' % json.dumps(self.AirOK))
        #message.append('"front_door_closed":%s,' % json.dumps(self.front_door_closed)) uncomment when this is used
        #message.append('"notUsed7":%s,' % json.dumps(self.notUsed7)) uncomment when this is used
        message.append('"LN2-en":%s}' % json.dumps(self.LN2en))
        self.__lock.release()
        return ''.join(message)
