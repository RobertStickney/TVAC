import time
import math
from datetime import datetime
from DataContracts.PfeifferGuageContract import PfeifferGuageContract

class PfeifferGuageCollection:

    def __init__(self):
        self.time = datetime.now()


        pass #fill this in

    def getParmValues(self, Address):
        ParmDict = {"041": self.Pfeiffer_GenCmdRead(Address, Parm=41),
                    "049": self.Pfeiffer_GenCmdRead(Address, Parm=49),
                    "303": self.Pfeiffer_GenCmdRead(Address, Parm=303),
                    "312": self.Pfeiffer_GenCmdRead(Address, Parm=312),
                    "349": self.Pfeiffer_GenCmdRead(Address, Parm=349),
                    "730": self.Pfeiffer_GenCmdRead(Address, Parm=730),
                    "732": self.Pfeiffer_GenCmdRead(Address, Parm=732),
                    "740": self.Pfeiffer_GenCmdRead(Address, Parm=740),
                    "741": self.Pfeiffer_GenCmdRead(Address, Parm=741),
                    "742": self.Pfeiffer_GenCmdRead(Address, Parm=742)}
        return ParmDict

    def getPressureValue(self, Address):
        PressureDict = {"pressure": self.Pfeiffer_GenCmdRead(Address, Parm=740)}
        return PressureDict


    #Functions copied from pfeiffer_guage_interface.py

    def Pfeiffer_applyChecksum(self, cmd):  # append the sum of the string's bytes mod 256 + '\r'
        return "{0}{1:03d}\r".format(cmd, self.Pfeiffer_GetChecksum(cmd))

    def Pfeiffer_GetChecksum(self, cmd):  # append the sum of the string's bytes mod 256 + '\r'
        return sum(cmd.encode()) % 256

    def Pfeiffer_GenCmdRead(self, Address, Parm=349):  # Cmd syntax see page #16 of MPT200 Operating instructions
        return self.Pfeiffer_applyChecksum("{:03d}00{:03d}02=?".format(Address, Parm))

    def Pfeiffer_ResponceGood(self, Address, Resp, Parm): #There was a mix of Repsonce and Resp -> Unified with Resp
        # print("R:--" + Responce.replace('\r', r'\r') + "---")
        if int(Resp[-3:]) != self.Pfeiffer_GetChecksum(Resp[:-3]):
            print("R:--" + Resp.replace('\r', r'\r') + "---",
                  "Checksum:" + str(self.Pfeiffer_GetChecksum(Resp[:-3])) + "Failure")
            return False
        if int(Resp[:3]) != Address:
            print("R:--" + Resp.replace('\r', r'\r') + "---", "Address:", str(Address), "Failure")
            return False
        if int(Resp[5:8]) != Parm:
            print("R:--" + Resp.replace('\r', r'\r') + "---", "Param:", str(Parm), "Failure")
            return False
        if int(Resp[8:10]) != (len(Resp) - 13):
            print("R:--" + Resp.replace('\r', r'\r') + "---", "Payload size:", str(len(Resp) - 13),
                  "Failure" + Resp[8:10])
            return False
        if (int(Resp[8:10]) == 6) and (Resp[10:-3] == 'NO_DEF'):
            print("R:--" + Resp.replace('\r', r'\r') + "---", "Error: The parameter", str(Parm), "does not exist.")
            return False
        if (int(Resp[8:10]) == 6) and (Resp[10:-3] == '_RANGE'):
            print("R:--" + Resp.replace('\r', r'\r') + "---",
                  "Error: Data length for param, " + str(Parm) + ", is outside the permitted range.")
            return False
        if (int(Resp[8:10]) == 6) and (Resp[10:-3] == '_LOGIC'):
            print("R:--" + Resp.replace('\r', r'\r') + "---", "Error: Logic access violation for the param:",
                  str(Parm))
            return False
        return True  # Yea!! respomnce seems ok

    def Pfeiffer_SendReceive(self, Address, Parm=349, dataStr=None):
        p_gauge = open('/dev/ttyxuart2', 'r+b', buffering=0)
        for tries in range(3):
            if dataStr is None:
                p_gauge.write(self.Pfeiffer_GenCmdRead(Address, Parm).encode())
            else:
                p_gauge.write(self.Pfeiffer_GenCmdWrite(Address, Parm, dataStr).encode())
            time.sleep(0.060 * (tries + 1))
            Resp = p_gauge.read(113 * (tries + 1)).decode().strip()
            if self.Pfeiffer_ResponceGood(Address, Resp, Parm):
                break
            print("Try number: " + str(tries))
        else:
            print("No more tries! Something is wrong!")
            Resp = "{:*^32}".format('Timeout!')
        p_gauge.close
        return Resp[10:-3]

    def Pfeiffer_Convert_Str2Press(self, buff, inTorr=True):
        if (len(buff) == 6 and buff.isdigit):
            p = float((float(buff[:4]) / 1000.0) * float(10 ** (int(buff[-2:]) - 20)))
            if inTorr:  ## Return the Pressure in Torr.
                return p * 0.75006  # hPa to Torr
            else:  ## Return in hPa gauge default.
                return p
        print('Data: ' + buff + '')
        return 0

    def Pfeiffer_GetPressure(self, Address, inTorr = True): # Pfeifer returns pressure in hPa
        return self.Pfeiffer_Convert_Str2Press(self.Pfeiffer_SendReceive(Address, 740), inTorr)

    def Pfiefer_GetSwPressure(self, Address, sw2=False, inTorr = True):
        if sw2:
            return self.Pfeiffer_Convert_Str2Press(self.Pfeiffer_SendReceive(Address, 732), inTorr)
        else:
            return self.Pfeiffer_Convert_Str2Press(self.Pfeiffer_SendReceive(Address, 730), inTorr)

    def Pfiefer_SetSwPressure(self, Pressure, Address, sw2=False, inTorr = True):
        dataStr = self.Pfeiffer_Convert_Press2Str(Pressure, inTorr)
        if sw2:
            resp = self.Pfeiffer_SendReceive(Address,732,dataStr)
        else:
            resp = self.Pfeiffer_SendReceive(Address,730,dataStr)
        if dataStr != resp:
            print("Error Setting Switch pressure.")

    def dataRequest(self,Address, Parm=349):
        p_gauge = open('/dev/ttyxuart0', 'r+b', buffering=0)
        for tries in range(3):
            p_gauge.write(self.genCmdRead(Address, Parm).encode())
            time.sleep(0.060 * (tries + 1))
            Resp = p_gauge.read(113 * (tries + 1)).decode().strip()
            if self.responceGood(Address, Resp, Parm):
                break
            print("Try number: " + str(tries))
        else:
            print("No more tries! Something is wrong!")
            Resp = "{:*^32}".format('Timeout!')
        p_gauge.close
        return Resp[10:-3]
