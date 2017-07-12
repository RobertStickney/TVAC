import time
import json

from ZoneContract import ZoneContract
from ProfileInstance import ZonesInstance


class ShiMcc:

    def getChecksum(self,cmd):  # append the sum of the string's bytes mod 256 + '\r'
        d = sum(cmd.encode())
        contractObj = ZoneContract(json.loads('{"zone":6,"temp":"updateing"}'))
        zonesInstance = ZonesInstance.getInstance()
        zonesInstance.zones.update(contractObj)
        time.sleep(60)
        contractObj2 = ZoneContract(json.loads('{"zone":6,"temp":"updated"}'))
        zonesInstance.zones.update(contractObj2)
        #       0x30 + ( (d2 to d6) or (d0 xor d6) or ((d1 xor d7) shift to d2)
        return 0x30 + ((d & 0x3c) |
                       ((d & 0x01) ^ ((d & 0x40) >> 6)) |  # (d0 xor d6)
                       ((d & 0x02) ^ ((d & 0x80) >> 6)))  # (d1 xor d7)

    def genCmd(self,cmd):  # Cmd syntax see page MCC Programing Guide
        return "${0}{1:c}\r".format(cmd, self.getChecksum(cmd))

    def responceGood(self, Responce):
        print("R:--" + Responce.replace('\r', r'\r') + "---")
        if Responce[-1] != '\r':
            print("R:--" + Responce.replace('\r', r'\r') + "--- Missing Carriage Return at the end")
            return False
        # print("Checksum: '" + Responce[-2] + "' Data: '" + Responce[1:-2] + "' Calc cksum: '" + chr(GetChecksum(Responce[1:-2])) + "'")
        if Responce[-2] != chr(self.getChecksum(Responce[1:-2])):
            print("R:--" + Responce.replace('\r', r'\r') + "---", "Checksum: " + chr(self.getChecksum(Responce[1:-2])))
            return False
        if Responce[0] != '$':
            print("R:--" + Responce.replace('\r', r'\r') + "---", "'$' is not the first byte!")
            return False
        return True  # Yea!! responce seems ok

    def sendCmd(self,Command):
        MCC = open('/dev/ttyxuart2', 'r+b', buffering=0)
        for tries in range(3):
            MCC.write(self.genCmd(Command).encode())
            time.sleep(0.10 * (tries + 1))
            print("C:--" + self.genCmd(Command).replace('\r', r'\r') + "---")
            resp = MCC.read(64).decode()
            if self.responceGood(resp):
                if resp[1] == 'A':  # Responce Good!
                    Data = self.format_Responce(resp[2:-2])
                elif resp[1] == 'B':
                    Data = self.format_Responce(resp[2:-2], pwrFail=True)
                elif resp[1] == 'E':
                    Data = self.format_Responce(resp[2:-2], error=True)
                elif resp[1] == 'F':
                    Data = self.format_Responce(resp[2:-2], error=True, pwrFail=True)
                else:
                    Data = self.format_Responce("R--" + resp + "-- unknown", error=True)
                break
            print("Try number: " + str(tries))
        else:
            print("No more tries! Something is wrong!")
            Data = self.format_Responce('Timeout!', error=True)
        MCC.close
        return Data

    def getStatus(self):
        # Create Dict of Functions
        FunS = {"Status": self.getStatus,
                "TcPressure": self.getTcPressure,
                "TempStage1": self.getFirstStageTemp,
                "TempStage2": self.getSecondStageTemp,
                "Duty Cycle": self.getDutyCycle,
                "RegenStep": self.getRegenStep,
                "RegenError": self.getRegenError,
                "CryoPumpRdyState": self.getCryoPumpRdyState}
        return self.runGetFunctions(FunS)

    def getParamValues(self):
        # Create Dict of Functions
        FunS = {"MCCVersion": self.getModuleVersion,
                "ElapsedTime": self.getElapsedTime,
                "FirstStageTempCTL": self.getFirstStageTempCTL,
                "PurgeValveState": self.getPurgeValveState,
                "RegenCycles": self.getRegenCycles,
                "RegenParam_0": self.getRegenParam_0,
                "RegenParam_1": self.getRegenParam_1,
                "RegenParam_2": self.getRegenParam_2,
                "RegenParam_3": self.getRegenParam_3,
                "RegenParam_4": self.getRegenParam_4,
                "RegenParam_5": self.getRegenParam_5,
                "RegenParam_6": self.getRegenParam_6,
                "RegenParam_A": self.getRegenParam_A,
                "RegenParam_C": self.getRegenParam_C,
                "RegenParam_G": self.getRegenParam_G,
                "RegenParam_z": self.getRegenParam_z,
                "RegenTime": self.getRegenTime,
                "RoughingValveState": self.getRoughingValveState,
                "RoughingInterlock": self.getRoughingInterlock,
                "SecondStageTempCTL": self.getSecondStageTempCTL,
                "TcPressureState": self.getTcPressureState}
        return self.runGetFunctions(FunS)

    def runGetFunctions(self,Functions):
        er = False;
        pf = False;
        vals = {}
        for key in Functions.keys():
            val = Functions[key]()
            er |= val['Error']
            pf |= val['PowerFailure']
            vals[key] = val['Data']
        return self.formatResponce(json.dumps(vals), er, pf)

    def formatResponce(self,d, error=False, pwrFail=False):
        return {"Error": error, "PowerFailure": pwrFail, "Data": d}

    def getDutyCycle(self):  # Command Ex: "$XOI??_\r"
        return self.sendCmd("XOI??")

    def getElapsedTime(self):  # Command Ex: "$Y?J\r"
        return self.sendCmd("Y?")

    def getFirstStageTemp(self):  # Command Ex: "$J;\r"
        return self.sendCmd("J")

    def getFirstStageTempCTL(self):  # Command Ex: "$H?5\r"
        return self.sendCmd("H?")

    def setFirstStageTempCTL(self, temp = 0, method = 0):
        if (temp < 0) | (temp > 320):
            print('First stage Temperature out is of range (0-320): {:d}'.format(temp))
            return self.formatResponce("Temp out of range: "+str(temp), error = True)
        if (method < 0) | (method > 3):
            print('First stage control method is out of range (0-3): {:d}'.format(method))
            return self.formatResponce("Temp out of range: "+str(method), error = True)
        # add convert to real data
        return self.sendCmd("H{0:d},{1:d}".format(temp, method))

    def getModuleVersion(self):  # Command Ex: "$@1\r"
        return self.sendCmd("@")

    def getCryoPumpOnState(self):  # Command Ex: "$A?2\r"
        return self.sendCmd("A?")

    def getCryoPumpRdyState(self):  # Command Ex: "$A??m\r"
        return self.sendCmd("A??")

    def turnCryoPumpOn(self):  # Command Ex: "$A1c\r"
        return self.sendCmd("A1")

    def turnCryoPumpOff(self):
        return self.sendCmd("A0")

    def getPurgeValveState(self):  # Command Ex: "$E?6\r"
        return self.sendCmd("E?")

    def openPurgeValve(self):
        return self.sendCmd("E1")

    def closePurgeValve(self):  # Command Ex: "$E0d\r"
        return self.sendCmd("E0")

    def startRegen(self,num):
        if (num < 0) | (num > 4):
            print('First stage control method is out of range (0-3): {:d}'.format(method))
            return self.formatResponce("Temp out of range: " + str(method), error=True)
        return self.sendCmd("N{0:d}".format(num))

    def getRegenCycles(self):  # Command Ex: "$Z?K\r"
        return self.sendCmd("Z?")

    def getRegenError(self):  # Command Ex: "$eT\r"
        return self.sendCmd("e")

    def getRegenParam0(self):
        return self.sendCmd("P0?")

    def getRegenParam_1(self):
        return self.sendCmd("P1?")

    def getRegenParam_2(self):
        return self.sendCmd("P2?")

    def getRegenParam_3(self):
        return self.sendCmd("P3?")

    def getRegenParam_4(self):
        return self.sendCmd("P4?")

    def getRegenParam_5(self):
        return self.sendCmd("P5?")

    def getRegenParam_6(self):
        return self.sendCmd("P6?")

    def getRegenParam_A(self):
        return self.sendCmd("PA?")

    def getRegenParam_C(self):
        return self.sendCmd("PC?")

    def getRegenParam_G(self):
        return self.sendCmd("PG?")

    def getRegenParam_z(self):
        return self.sendCmd("Pz?")

    def setRegenParam(self,Param, Value):
        if (int(Param) == '0') & ((Value < 0) | (Value > 59994)):
            return self.formatResponce("RegenParam: Pump Restart Delay out of range: " + str(Value), error=True)
        elif (int(Param) == '1') & ((Value < 0) | (Value > 9990)):
            return self.formatResponce("RegenParam: Extend Purge time out of range: " + str(Value), error=True)
        elif (int(Param) == '2') & ((Value < 0) | (Value > 200)):
            return self.formatResponce("RegenParam: Repurge Cycles out of range: " + str(Value), error=True)
        elif (int(Param) == '3') & ((Value < 25) | (Value > 200)):
            return self.formatResponce("RegenParam: Rough to Pressure out of range: " + str(Value), error=True)
        elif (int(Param) == '4') & ((Value < 1) | (Value > 100)):
            return self.formatResponce("RegenParam: Rate of Rise out of range: " + str(Value), error=True)
        elif (int(Param) == '5') & ((Value < 0) | (Value > 200)):
            return self.formatResponce("RegenParam: Rate of Rise Cycles out of range: " + str(Value), error=True)
        elif (int(Param) == '6') & ((Value < 0) | (Value > 80)):
            return self.formatResponce("RegenParam: Restart Temperature out of range: " + str(Value), error=True)
        elif (str(Param) == 'A') & ((Value < 0) | (Value > 1)):
            return self.formatResponce("RegenParam: Roughing Interlock not 0 or 1: " + str(Value), error=True)
        elif (str(Param) == 'C') & ((Value < 1) | (Value > 3)):
            return self.formatResponce("RegenParam: Pumps per Compressor: " + str(Value), error=True)
        elif (str(Param) == 'G') & ((Value < 0) | (Value > 9999)):
            return self.formatResponce("RegenParam: Repurge time out of range: " + str(Value), error=True)
        elif (str(Param) == 'z') & ((Value < 0) | (Value > 1)):
            return self.formatResponce("RegenParam: Stand by mode not 0 or 1: " + str(Value), error=True)
        else:
            return self.formatResponce("Parameter out of range: " + str(Param), error=True)
        return self.sendCmd("P" + str(Param) + str(Value))

    def getRegenStep(self):  # Command Ex: "$O>\r"
        return self.sendcmd("O")

    def getRegenStepTimer(self):  # Command Ex: "$kZ\r"
        return self.sendCmd("k")

    def getRegenTime(self):  # Command Ex: "$aP\r"
        return self.sendCmd("a")

    def getRoughingValveState(self):  # Command Ex: "$D?3\r"
        return self.sendCmd("D?")

    def openRoughingValve(self):  # Command Ex: "$D1d\r"
        return self.sendCmd("D1")

    def closeRoughingValve(self):
        return self.sendCmd("D0")

    def getRoughingInterlock(self):  # Command Ex: "$Q?B\r"
        return self.sendCmd("Q?")

    def clearRoughingInterlock(self):  # Command Ex: "$Q?B\r"
        return self.sendCmd("Q")

    def getSecondStageTemp(self):  # Command Ex: "$K:\r"
        return self.sendCmd("K")

    def getSecondStageTempCTL(self):  # Command Ex: "$I?:\r"
        return self.sendCmd("I?")

    def setSecondStageTempCTL(self, temp):  # Command Ex: "$I?:\r"
        if (temp < 0) | (temp > 320):
            print('Second stage Temperature out is of range (0-320): {:d}'.format(temp))
            return self.formatResponce("Temp out of range: " + str(temp), error=True)
        return self.sendCmd("I{0:d}".format(temp))

    def getStatus(self):  # Command Ex: "$S16\r"
        return self.sendCmd("S1")

    def getTcPressureState(self):  # Command Ex: "$B?3\r"
        return self.sendCmd("B?")

    def turnTcPressureOn(self):  # Command Ex: "$B1b\r"
        return self.sendCmd("B1")

    def turnTcPressureOff(self):  # Command Ex: "$B?3\r"
        return self.sendCmd("B0")

    def getTcPressure(self):  # Command Ex: "$L=\r"
        return self.sendCmd("L")
