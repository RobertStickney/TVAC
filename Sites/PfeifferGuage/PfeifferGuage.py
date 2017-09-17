#!/usr/bin/env python3.5
import time
import math


class PfeifferGuage:

    def GetChecksum(self, cmd):  # append the sum of the string's bytes mod 256 + '\r'
        return sum(cmd.encode()) % 256

    def applyChecksum(self, cmd):  # append the sum of the string's bytes mod 256 + '\r'
        return "{0}{1:03d}\r".format(cmd, self.GetChecksum(cmd))

    def GenCmdRead(self, Address, Parm=349):  # Cmd syntax see page #16 of MPT200 Operating instructions
        return self.applyChecksum("{:03d}00{:03d}02=?".format(Address, Parm))

    def GenCmdWrite(self, Address, Parm, dataStr):  # Cmd syntax on page #16 of MPT200 Operating instructions
        return self.applyChecksum("{0:03d}10{1:03d}{2:02d}{3}".format(Address, Parm, len(dataStr), dataStr))

    def ResponceGood(self, Address, Responce, Parm=349):
        # print("R:--" + Responce.replace('\r', r'\r') + "---")
        if int(Responce[-3:]) != self.GetChecksum(Responce[:-3]):
            print("R:--" + Responce.replace('\r', r'\r') + "---",
                  "Checksum:" + str(self.GetChecksum(Responce[:-3])) + "Failure")
            return False
        if int(Responce[:3]) != Address:
            print("R:--" + Responce.replace('\r', r'\r') + "---", "Address:", str(Address), "Failure")
            return False
        if int(Responce[5:8]) != Parm:
            print("R:--" + Responce.replace('\r', r'\r') + "---", "Param:", str(Parm), "Failure")
            return False
        if int(Responce[8:10]) != (len(Responce) - 13):
            print("R:--" + Responce.replace('\r', r'\r') + "---", "Payload size:", str(len(Responce) - 13),
                  "Failure" + Responce[8:10])
            return False
        if (int(Responce[8:10]) == 6) and (Responce[10:-3] == 'NO_DEF'):
            print("R:--" + Responce.replace('\r', r'\r') + "---", "Error: The parameter", str(Parm), "does not exist.")
            return False
        if (int(Responce[8:10]) == 6) and (Responce[10:-3] == '_RANGE'):
            print("R:--" + Responce.replace('\r', r'\r') + "---",
                  "Error: Data length for param, " + str(Parm) + ", is outside the permitted range.")
            return False
        if (int(Responce[8:10]) == 6) and (Responce[10:-3] == '_LOGIC'):
            print("R:--" + Responce.replace('\r', r'\r') + "---", "Error: Logic access violation for the param:",
                  str(Parm))
            return False
        return True  # Yea!! respomnce seems ok

    def Convert_Str2Press(self, buff, inTorr=True):
        if (len(buff) == 6 and buff.isdigit):
            p = float((float(buff[:4]) / 1000.0) * float(10 ** (int(buff[-2:]) - 20)))
            if inTorr:  ## Return the Pressure in Torr.
                return p * 0.75006  # hPa to Torr
            else:  ## Return in hPa gauge default.
                return p
        print('Data: ' + buff + '')
        return 0

    def Convert_Press2Str(self, pressure, inTorr=True):
        if inTorr:
            pressure = pressure / 0.75006
        b = math.floor(math.log10(pressure))
        if b < -20:  ## coarse minimum power of 10 to -20
            b = -20
        if b > 79:  ## coarse maximum power of 10 to 79
            b = 79
        a = int(1000.0 * (pressure / (10 ** b)))
        return "{:04d}{:02d}".format(a, b + 20)

    def SendReceive(self, Address, Parm=349, dataStr=None):
        p_gauge = open('/dev/ttyxuart2', 'r+b', buffering=0)
        for tries in range(3):
            if dataStr is None:
                p_gauge.write(self.GenCmdRead(Address, Parm).encode())
            else:
                p_gauge.write(self.GenCmdWrite(Address, Parm, dataStr).encode())
            time.sleep(0.060 * (tries + 1))
            Resp = p_gauge.read(113 * (tries + 1)).decode().strip()
            if self.ResponceGood(Address, Resp, Parm):
                break
            print("Try number: " + str(tries))
        else:
            print("No more tries! Something is wrong!")
            Resp = "{:*^32}".format('Timeout!')
        p_gauge.close()
        return Resp[10:-3]

    def GetPressure(self, Address, inTorr=True):  # Pfeifer returns pressure in hPa
        return self.Convert_Str2Press(self.SendReceive(Address, 740), inTorr)

    def GetSwPressure(self, Address, sw2=False, inTorr=True):
        if sw2:
            return self.Convert_Str2Press(self.SendReceive(Address, 732), inTorr)
        else:
            return self.Convert_Str2Press(self.SendReceive(Address, 730), inTorr)

    def SetSwPressure(self, Pressure, Address, sw2=False, inTorr=True):
        dataStr = self.Convert_Press2Str(Pressure, inTorr)
        if sw2:
            resp = self.SendReceive(Address, 732, dataStr)
        else:
            resp = self.SendReceive(Address, 730, dataStr)
        if dataStr != resp:
            print("Error Setting Switch pressure.")

