#!/usr/bin/env python3


def SHI_MCC_GetChecksum(cmd):    #append the sum of the string's bytes mod 256 + '\r'
    d = sum(cmd.encode())
    #       0x30 + ( (d2 to d6) or (d0 xor d6) or ((d1 xor d7) shift to d2)                            
    return  0x30 + ( (d & 0x3c) | 
    				((d & 0x01) ^ ((d & 0x40) >> 6)) | # (d0 xor d6)
    				((d & 0x02) ^ ((d & 0x80) >> 6)) ) # (d1 xor d7)

def SHI_MCC_GenCmd(cmd): #Cmd syntax see page MCC Programing Guide
    return "${0}{1:c}\r".format(cmd, SHI_MCC_GetChecksum(cmd))

print(SHI_MCC_GenCmd("XOI??").replace('\r', r'\r'))
print(SHI_MCC_GenCmd("A23").replace('\r', r'\r'))
print(SHI_MCC_GenCmd("Y?").replace('\r', r'\r'))
print(SHI_MCC_GenCmd("A+001150").replace('\r', r'\r'))
print(SHI_MCC_GenCmd("m").replace('\r', r'\r'))
print(SHI_MCC_GenCmd("A+1").replace('\r', r'\r'))
print(SHI_MCC_GenCmd("l").replace('\r', r'\r'))
print(SHI_MCC_GenCmd("J").replace('\r', r'\r'))
print(SHI_MCC_GenCmd("A+0064.0").replace('\r', r'\r'))
print(SHI_MCC_GenCmd("").replace('\r', r'\r'))
