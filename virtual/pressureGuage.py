from socket import *
import serial


tty = serial.Serial('/dev/ttyUSB0', 9600, timeout=.5)


def RSoIP():
    buff,rsp='',''
    print("Start")
    try:
        while buff != '\r':
            print("About to read from tty")
            print(tty.inWaiting())
            buff=tty.read(size=1)
            print("Read from ttyUSB0")
            print(buff)
            rsp += buff
        if len(rsp) == 0:
            return True
        # a.sendto(rsp,"test")
    except timeout: return True
    return True


x = True
while x:
    x=RSoIP()

