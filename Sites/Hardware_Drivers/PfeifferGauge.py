#!/usr/bin/env python3.5
from socket import *
import time
import math


class PfeifferGauge:

    def __init__(self):
        self.a = socket(AF_INET, SOCK_DGRAM)

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
            if p > 1e-10:
                if inTorr:  ## Return the Pressure in Torr.
                    return p * 0.75006  # hPa to Torr
                else:  ## Return in hPa gauge default.
                    return p
            else:
                raise ValueError("Convert_Str2Press value of %s below realistic value" % p)
        else:
            raise ValueError("Convert_Str2Press value in: %s" % buff)

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
        for tries in range(3):
            ip = '192.168.99.124'
            ip = 'localhost'
            if dataStr is None:
                tmp = self.GenCmdRead(Address, Parm).encode()
                print("messing sending: {}".format(tmp))
                self.a.sendto(tmp, (ip, 1234))
                print("after send")
            else:
                self.a.sendto(self.GenCmdWrite(Address, Parm, dataStr).encode(), (ip, 1234))
            time.sleep(0.060 * (tries + 1))
            print("about to wait for reply")
            Responce,_ = self.a.recvfrom(4092)
            Resp = Responce.decode().strip()
            print("reply: "+Resp)
            if self.ResponceGood(Address, Resp, Parm):
                break
            print("Try number: " + str(tries))
        else:
            print("No more tries! Something is wrong!")
            Resp = "{:*^32}".format('Timeout!')
        return Resp[10:-3]

    def SendReceive_Xuart(self, Address, Parm=349, dataStr=None):
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

    def GetCCstate(self, Address):  # Is the Cold Cathode Sensor on
        buff = self.SendReceive(Address, 41)
        if buff == '0':
            return False
        elif buff == '1':
            return True
        else:
            raise ValueError("GetCCstate value not 0 or 1: %s" % buff)

    def SetCCstate(self, Address, CC_on):  # Set the Cold Cathode Sensor to on.
        if CC_on == False:
            resp = self.SendReceive(Address, 41, '0')
            if resp != '0':
                raise ValueError("SetCCstate value not set to 0: %s" % resp)
        else:
            resp = self.SendReceive(Address, 41, '1')
            if resp != '1':
                raise ValueError("SetCCstate value not set to 1: %s" % resp)

    def GetSwMode(self, Address):  # Get Cold Cathode switching range
        buff = self.SendReceive(Address, 49)
        if buff.isdigit:
            return int(buff)
        else:
            raise ValueError("GetSwMode value not 0 or 1: %s" % buff)

    def SetSwMode(self, Address, CC_on):  # Set the Cold Cathode switching range to trans_LO.
        if CC_on == False:
            resp = self.SendReceive(Address, 49, '000')  # switch
            if resp != '000':
                raise ValueError("GetSwMode value not set to 0: %s" % resp)
        else:
            resp = self.SendReceive(Address, 49, '001')  # trans_LO
            if resp != '001':
                raise ValueError("GetSwMode value not set to 1: %s" % resp)

    def GetError(self, Address):  # Pfeifer returns an error in the gauge
        return self.SendReceive(Address, 303)

    def GetSofwareV(self, Address):  # Returns gauge's software version
        return self.SendReceive(Address, 312)

    def GetModelName(self, Address):  # Returns gauge's model name
        return self.SendReceive(Address, 349)

    def GetSwPressure(self, Address, sw2=False, inTorr=True):
        if sw2:
            return self.Convert_Str2Press(self.SendReceive(Address, 732), inTorr)
        else:
            return self.Convert_Str2Press(self.SendReceive(Address, 730), inTorr)

    def SetSwPressure(self, Address, Pressure, sw2=False, inTorr=True):
        dataStr = self.Convert_Press2Str(Pressure, inTorr)
        if sw2:
            resp = self.SendReceive(Address, 732, dataStr)
        else:
            resp = self.SendReceive(Address, 730, dataStr)
        if dataStr != resp:
            raise  ValueError("Error Setting Switch pressure. sent: '{}'; resp '{}'".format(dataStr,resp))

    def GetPressure(self, Address, inTorr=True):  # Pfeifer gauge returns pressure in hPa or Torr
        return self.Convert_Str2Press(self.SendReceive(Address, 740), inTorr)

    def SetPressure(self, Address, Pressure, inTorr=True):  # Set pressure in hPa or Torr for calibration.
        dataStr = self.Convert_Press2Str(Pressure, inTorr)
        resp = self.SendReceive(Address, 740, dataStr)
        if dataStr != resp:
            raise  ValueError("Error Setting pressure. Sent: '{}'; Resp: '{}'".format(dataStr,resp))

    def SetPressureSp(self, Address, value):
        if value > 999:
            value = 999
        elif value < 0:
            value = 0
        dataStr = "{:03d}".format(int(value))
        resp = self.SendReceive(Address, 741, dataStr)
        if dataStr != resp:
            raise  ValueError("Error Setting pressure. Sent: '{}'; Resp: '{}'".format(dataStr,resp))

    def GetCorrPir(self, Address):  # Get Pirani Correction Value
        return float(self.SendReceive(Address, 742))

    def SetCorrPir(self, Address, value):  # Setting Pirani Correction Value
        if value > 8.0:
            value = 8.0
        elif value < 0.2:
            value = 0.2
        dataStr = "{:06d}".format(int(value*100))
        resp = self.SendReceive(Address, 742, dataStr)
        if dataStr != resp:
            raise  ValueError("Error Setting Pirani Correction Value. Sent: '{}'; Resp: '{}'".format(dataStr,resp))

    def GetCorrCC(self, Address):  # Get Cold Cathode Correction Value
        return float(self.SendReceive(Address, 742))

    def SetCorrCC(self, Address, value):  # Setting Cold Cathode Correction Value
        if value > 8.0:
            value = 8.0
        elif value < 0.2:
            value = 0.2
        dataStr = "{:06d}".format(int(value*100))
        resp = self.SendReceive(Address, 742, dataStr)
        if dataStr != resp:
            raise  ValueError("Error Setting Cold Cathode Correction Value. Sent: '{}'; Resp: '{}'".format(dataStr,resp))

if __name__ == '__main__':
    import sys

    sys.path.insert(0, '../')
    pg = PfeifferGauge()
    for i in range(1, 3+1):
        print("Addr {:d}, {}, Pressure: {:f} torr.".format(i,
                                                           pg.GetModelName(i),
                                                           pg.GetPressure(i)))
