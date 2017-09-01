import time

class PfeifferGuage:

    def getChecksum(self,cmd):  # append the sum of the string's bytes mod 256 + '\r'
        return sum(cmd.encode()) % 256

    def applyChecksum(self,cmd):  # append the sum of the string's bytes mod 256 + '\r'
        return "{0}{1:03d}\r".format(cmd, self.getChecksum(cmd))

    def genCmdRead(self,Address, Parm=349):  # Cmd syntax see page #16 of MPT200 Operating instructions
        return self.applyChecksum("{:03d}00{:03d}02=?".format(Address, Parm))

    # Why is this never used?
    def genCmdWrite(self,Address, Parm, dataStr):  # Cmd syntax on page #16 of MPT200 Operating instructions
        return self.applyChecksum("{0:03d}10{1:03d}{2:02d}{3}".format(Address, Parm, len(dataStr), dataStr))

    def responceGood(self,Address, Responce, Parm=349):
        # print("R:--" + Responce.replace('\r', r'\r') + "---")
        if int(Responce[-3:]) != self.getChecksum(Responce[:-3]):
            print("R:--" + Responce.replace('\r', r'\r') + "---",
                  "Checksum:" + str(self.getChecksum(Responce[:-3])) + "Failure")
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
        return True  # Yea!! respomnce seems ok

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
        p_gauge.close()
        return Resp[10:-3]

    def getPressure(self,Address):  # Pfeifer returns pressure in hPa
        buff = self.dataRequest(Address, 740)
        if (len(buff) == 6 and buff.isdigit):
            return float((int(buff[:4]) / 1000) * 10 ** (int(buff[-2:]) - 20))
        print('Data: ' + buff + '')
        return buff