#!/usr/bin/env python3
# SHI_MCC_Interface
import io
import time

def SHI_MCC_GetChecksum(cmd):    #append the sum of the string's bytes mod 256 + '\r'
    d = sum(cmd.encode())
    #       0x30 + ( (d2 to d6) or (d0 xor d6) or ((d1 xor d7) shift to d2)                            
    return  0x30 + ( (d & 0x3c) | 
                    ((d & 0x01) ^ ((d & 0x40) >> 6)) | # (d0 xor d6)
                    ((d & 0x02) ^ ((d & 0x80) >> 6)) ) # (d1 xor d7)

def SHI_MCC_GenCmd(cmd): #Cmd syntax see page MCC Programing Guide
    return "${0}{1:c}\r".format(cmd, SHI_MCC_GetChecksum(cmd))

def SHI_MCC_ResponceGood(Responce):
    print("R:--" + Responce.replace('\r', r'\r') + "---")
    if Responce[-1] != '\r':
        print("R:--" + Responce.replace('\r', r'\r') + "--- Missing Carriage Return at the end")
        return False
    print("Checksum: " + Responce[-2:-1], "Data: " + Responce[1:-2])
    if int(Responce[-2]) != SHI_MCC_GetChecksum(Responce[1:-3]):
        print("R:--" + Responce.replace('\r', r'\r') + "---","Checksum: " + str(SHI_MCC_GetChecksum(Responce[1:-3])))
        return False
    if int(Responce[0]) != '$':
        print("R:--" + Responce.replace('\r', r'\r') + "---","'$' is not the first byte!")
        return False
    return True # Yea!! responce seems ok

def SHI_MCC_cmd(Command):
    MCC = open('/dev/ttyxuart2', 'r+b', buffering=0)
    Data = {"Error"=False, "PowerFailure"=False, "Data"=""}
    for tries in range(3):
        MCC.write(SHI_MCC_GenCmd(Command).encode())
        time.sleep(0.10(tries+1))
        print("C:--" + SHI_MCC_GenCmd(Command).replace('\r', r'\r') + "---")
        resp = p_gauge.read(64).decode()
        if SHI_MCC_ResponceGood(resp):
            break
        print("Try number: " + str(tries))
    else:
        print("No more tries! Something is wrong!")
        Data["Error"] = True
        Data["Data"] = 'Timeout!'
    MCC.close
    #if resp[1] = 'A': # Responce Good!
    if Data[1] = 'B':
        Data['PowerFailure'] = True
    if Data[1] = 'E':
        Data["Error"] = True
    if Data[1] = 'F':
        Data["Error"] = True
        Data['PowerFailure'] = True
    Data['data'] = resp[1:-3]
    return Data

