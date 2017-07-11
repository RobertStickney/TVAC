#!/usr/bin/env python3
# Pfeiffer_guage_Interface
import io
import time


def Pfeiffer_Vac_OLD(Command):
    p_gauge = open('/dev/ttyxuart0', 'r+b', buffering=0)
    p_gauge.write(Command.encode())
    time.sleep(0.060)
    temp = p_gauge.read(113)
    print("R:--" + temp.decode().replace('\r', r'\r') + "---")
    return temp.decode()

def Pfeiffer_GetChecksum(cmd):  #append the sum of the string's bytes mod 256 + '\r'
    return sum(cmd.encode())%256

def Pfeiffer_applyChecksum(cmd):  #append the sum of the string's bytes mod 256 + '\r'
    return "{0}{1:03d}\r".format(cmd, Pfeiffer_GetChecksum(cmd))

def Pfeiffer_GenCmdRead(Address, Parm=349): #Cmd syntax see page #16 of MPT200 Operating instructions
    return Pfeiffer_applyChecksum("{:03d}00{:03d}02=?".format(Address, Parm))

def Pfeiffer_GenCmdWrite(Address,Parm,dataStr): #Cmd syntax on page #16 of MPT200 Operating instructions
    return Pfeiffer_applyChecksum("{0:03d}10{1:03d}{2:02d}{3}".format(Address, Parm, len(dataStr), dataStr))

def Pfeiffer_ResponceGood_OLD(Address, Responce, Parm=349):
    print("R:--" + Responce.replace('\r', r'\r') + "---")
    if Responce[-1] != '\r':
        print("R:--" + Responce.replace('\r', r'\r') + "--- Missing Carriage Return at the end")
        return False
    if int(Responce[-4:-1]) != Pfeiffer_GetChecksum(Responce[:-4]):
        print("R:--" + Responce.replace('\r', r'\r') + "---","Checksum:" + str(Pfeiffer_GetChecksum(Responce[:-4])) + "Failure")
        return False
    if int(Responce[:3]) != Address:
        print("R:--" + Responce.replace('\r', r'\r') + "---","Address:",str(Address),"Failure")
        return False
    if int(Responce[5:8]) != Parm:
        print("R:--" + Responce.replace('\r', r'\r') + "---","Param:",str(Parm),"Failure")
        return False
    if int(Responce[8:10]) != (len(Responce) - 14):
        print("R:--" + Responce.replace('\r', r'\r') + "---","Payload size:",str(len(Responce) - 14),"Failure"+Responce[8:10])
        return False
    return True # Yea!! respomnce seems ok

def Pfeiffer_ResponceGood(Address, Responce, Parm=349):
    #print("R:--" + Responce.replace('\r', r'\r') + "---")
    if int(Responce[-3:]) != Pfeiffer_GetChecksum(Responce[:-3]):
        print("R:--" + Responce.replace('\r', r'\r') + "---","Checksum:" + str(Pfeiffer_GetChecksum(Responce[:-3])) + "Failure")
        return False
    if int(Responce[:3]) != Address:
        print("R:--" + Responce.replace('\r', r'\r') + "---","Address:",str(Address),"Failure")
        return False
    if int(Responce[5:8]) != Parm:
        print("R:--" + Responce.replace('\r', r'\r') + "---","Param:",str(Parm),"Failure")
        return False
    if int(Responce[8:10]) != (len(Responce) - 13):
        print("R:--" + Responce.replace('\r', r'\r') + "---","Payload size:",str(len(Responce) - 13),"Failure"+Responce[8:10])
        return False
    return True # Yea!! respomnce seems ok

def Pfeiffer_DataRequest(Address, Parm=349):
    p_gauge = open('/dev/ttyxuart0', 'r+b', buffering=0)
    for tries in range(3):
        p_gauge.write(Pfeiffer_GenCmdRead(Address,Parm).encode())
        time.sleep(0.060*(tries+1))
        Resp = p_gauge.read(113*(tries+1)).decode().strip()
        if Pfeiffer_ResponceGood(Address, Resp, Parm):
            break
        print("Try number: " + str(tries))
    else:
        print("No more tries! Something is wrong!")
        Resp = "{:*^32}".format('Timeout!')
    p_gauge.close
    return Resp[10:-3]

def Pfeiffer_GetPressure(Address): # Pfeifer returns pressure in hPa
    buff = Pfeiffer_DataRequest(Address, 740)
    if (len(buff)==6 and buff.isdigit):
        return float((int(buff[:4])/1000)*10**(int(buff[-2:])-20))
    print('Data: ' + buff + '')
