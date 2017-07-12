#!/usr/bin/env python3
# SHI_MCC_Interface
import io
import time
import json

def GetChecksum(cmd):    #append the sum of the string's bytes mod 256 + '\r'
    d = sum(cmd.encode())
    #       0x30 + ( (d2 to d6) or (d0 xor d6) or ((d1 xor d7) shift to d2)                            
    return  0x30 + ( (d & 0x3c) | 
                    ((d & 0x01) ^ ((d & 0x40) >> 6)) | # (d0 xor d6)
                    ((d & 0x02) ^ ((d & 0x80) >> 6)) ) # (d1 xor d7)

def GenCmd(cmd): #Cmd syntax see page MCC Programing Guide
    return "${0}{1:c}\r".format(cmd, GetChecksum(cmd))

def ResponceGood(Responce):
    print("R:--" + Responce.replace('\r', r'\r') + "---")
    if Responce[-1] != '\r':
        print("R:--" + Responce.replace('\r', r'\r') + "--- Missing Carriage Return at the end")
        return False
    #print("Checksum: '" + Responce[-2] + "' Data: '" + Responce[1:-2] + "' Calc cksum: '" + chr(GetChecksum(Responce[1:-2])) + "'")
    if Responce[-2] != chr(GetChecksum(Responce[1:-2])):
        print("R:--" + Responce.replace('\r', r'\r') + "---","Checksum: " + chr(GetChecksum(Responce[1:-2])))
        return False
    if Responce[0] != '$':
        print("R:--" + Responce.replace('\r', r'\r') + "---","'$' is not the first byte!")
        return False
    return True # Yea!! responce seems ok

def Send_cmd(Command):
    MCC = open('/dev/ttyxuart2', 'r+b', buffering=0)
    for tries in range(3):
        MCC.write(GenCmd(Command).encode())
        time.sleep(0.10*(tries+1))
        print("C:--" + GenCmd(Command).replace('\r', r'\r') + "---")
        resp = MCC.read(64).decode()
        if ResponceGood(resp):
            if resp[1] == 'A': # Responce Good!
                Data = Format_Responce(resp[2:-2])
            elif resp[1] == 'B':
                Data = Format_Responce(resp[2:-2], pwrFail = True)
            elif resp[1] == 'E':
                Data = Format_Responce(resp[2:-2], error = True)
            elif resp[1] == 'F':
                Data = Format_Responce(resp[2:-2], error = True, pwrFail = True)
            else:
                Data = Format_Responce("R--"+resp+"-- unknown", error = True)
            break
        print("Try number: " + str(tries))
    else:
        print("No more tries! Something is wrong!")
        Data = Format_Responce('Timeout!', error = True)
    MCC.close
    return Data

def get_Status():
    # Create Dict of Functions 
    FunS = {"Status"            : Get_Status,
            "TcPressure"        : Get_TcPressure,
            "TempStage1"        : Get_FirstStageTemp,
            "TempStage2"        : Get_SecondStageTemp,
            "Duty Cycle"        : Get_DutyCycle,
            "RegenStep"         : Get_RegenStep,
            "RegenError"        : Get_RegenError,
            "CryoPumpRdyState"  : Get_CryoPumpRdyState}
    return RunGetFunctions(FunS)

def get_ParamValues():
    # Create Dict of Functions 
    FunS = {"MCCVersion"        : Get_ModuleVersion,
            "ElapsedTime"       : Get_ElapsedTime,
            "FirstStageTempCTL" : Get_FirstStageTempCTL,
            "PurgeValveState"   : Get_PurgeValveState,
            "RegenCycles"       : Get_RegenCycles,
            "RegenParam_0"      : Get_RegenParam_0,
            "RegenParam_1"      : Get_RegenParam_1,
            "RegenParam_2"      : Get_RegenParam_2,
            "RegenParam_3"      : Get_RegenParam_3,
            "RegenParam_4"      : Get_RegenParam_4,
            "RegenParam_5"      : Get_RegenParam_5,
            "RegenParam_6"      : Get_RegenParam_6,
            "RegenParam_A"      : Get_RegenParam_A,
            "RegenParam_C"      : Get_RegenParam_C,
            "RegenParam_G"      : Get_RegenParam_G,
            "RegenParam_z"      : Get_RegenParam_z,
            "RegenTime"         : Get_RegenTime,
            "RoughingValveState": Get_RoughingValveState,
            "RoughingInterlock" : Get_RoughingInterlock,
            "SecondStageTempCTL": Get_SecondStageTempCTL,
            "TcPressureState"   : Get_TcPressureState}
    return RunGetFunctions(FunS)

def RunGetFunctions(Functions):
    er = False; pf = False; vals = {}
    for key in Functions.keys():
        val = Functions[key]()
        er |= val['Error']
        pf |= val['PowerFailure']
        vals[key] = val['Data']
    return Format_Responce(json.dumps(vals), er, pf)

def Format_Responce(d, error = False, pwrFail = False): # , d_int = 0, d_float = 0.0);
    return {"Error":error, "PowerFailure":pwrFail, "Data":d}  # , "int"=d_int, "float"=d_float}

# MCC Programmers References Guide Rev C 

# 2.4 • Duty Cycle pg:8
def Get_DutyCycle(): # Command Ex: "$XOI??_\r"
    #return (int(Send_cmd("XOI??"))/23) * 100 #check for int
    return Send_cmd("XOI??")

# 2.5 • Elapsed Time pg:8
def Get_ElapsedTime(): # Command Ex: "$Y?J\r"
    return Send_cmd("Y?")

# 2.5 • 

# 2.6 • 

# 2.7 • 

# 2.8 • First Stage Temperature pg:9
def Get_FirstStageTemp(): # Command Ex: "$J;\r"
    return Send_cmd("J")

# 2.9 • First Stage Temperature Control pg:10
def Get_FirstStageTempCTL(): # Command Ex: "$H?5\r"
    return Send_cmd("H?")
def Set_FirstStageTempCTL(temp = 0, method = 0):
    if (temp < 0) | (temp > 320):
        print('First stage Temperature out is of range (0-320): {:d}'.format(temp))
        return Format_Responce("Temp out of range: "+str(temp), error = True)
    if (method < 0) | (method > 3):
        print('First stage control method is out of range (0-3): {:d}'.format(method))
        return Format_Responce("Temp out of range: "+str(method), error = True)
    # add convert to real data
    return Send_cmd("H{0:d},{1:d}".format(temp, method))

# 2.10 • 

# 2.11 • Module Version pg:11
def Get_ModuleVersion(): # Command Ex: "$@1\r"
    return Send_cmd("@")

# 2.12 • 

# 2.13 • 

# 2.14 • Pump On/Off/Query pg:13
def Get_CryoPumpOnState(): # Command Ex: "$A?2\r"
    return Send_cmd("A?")
def Get_CryoPumpRdyState(): # Command Ex: "$A??m\r"
    return Send_cmd("A??")
def Turn_CryoPumpOn(): # Command Ex: "$A1c\r"
    return Send_cmd("A1")
def Turn_CryoPumpOff(): 
    return Send_cmd("A0")

# 2.15 • Purge On/Off/Query pg:14
def Get_PurgeValveState(): # Command Ex: "$E?6\r"
    return Send_cmd("E?")
def Open_PurgeValve(): 
    return Send_cmd("E1")
def Close_PurgeValve():  # Command Ex: "$E0d\r"
    return Send_cmd("E0")

# 2.16 • Regeneration pg:14
def Start_Regen(num):
    if (num < 0) | (num > 4):
        print('First stage control method is out of range (0-3): {:d}'.format(method))
        return Format_Responce("Temp out of range: "+str(method), error = True)
    return Send_cmd("N{0:d}".format(num))

# 2.17 • Regeneration Cycles pg:15
def Get_RegenCycles(): # Command Ex: "$Z?K\r"
    return Send_cmd("Z?")

# 2.18 • Regeneration Error pg:15
def Get_RegenError(): # Command Ex: "$eT\r"
    return Send_cmd("e")

# 2.19 • Regeneration Parameters pg:16
def Get_RegenParam_0():
    return Send_cmd("P0?")
def Get_RegenParam_1():
    return Send_cmd("P1?")
def Get_RegenParam_2():
    return Send_cmd("P2?")
def Get_RegenParam_3():
    return Send_cmd("P3?")
def Get_RegenParam_4():
    return Send_cmd("P4?")
def Get_RegenParam_5():
    return Send_cmd("P5?")
def Get_RegenParam_6():
    return Send_cmd("P6?")
def Get_RegenParam_A():
    return Send_cmd("PA?")
def Get_RegenParam_C():
    return Send_cmd("PC?")
def Get_RegenParam_G():
    return Send_cmd("PG?")
def Get_RegenParam_z():
    return Send_cmd("Pz?")
def Set_RegenParam(Param, Value): # expected call: Set_RegenParam(chr(int), int)
    if   (Param not in ['0', '1', '2', '3', '4', '5', '6', 'A', 'C', 'G', 'z']):
        return Format_Responce("Parameter out of range: "+str(Param), error = True)
    elif   (Param == '0') & ((Value < 0) | (Value > 59994)):
        return Format_Responce("RegenParam: Pump Restart Delay out of range: "+str(Value), error = True)
    elif (Param == '1') & ((Value < 0) | (Value > 9990)):
        return Format_Responce("RegenParam: Extend Purge time out of range: "+str(Value), error = True)
    elif (Param == '2') & ((Value < 0) | (Value > 200)):
        return Format_Responce("RegenParam: Repurge Cycles out of range: "+str(Value), error = True)
    elif (Param == '3') & ((Value < 25)| (Value > 200)):
        return Format_Responce("RegenParam: Rough to Pressure out of range: "+str(Value), error = True)
    elif (Param == '4') & ((Value < 1) | (Value > 100)):
        return Format_Responce("RegenParam: Rate of Rise out of range: "+str(Value), error = True)
    elif (Param == '5') & ((Value < 0) | (Value > 200)):
        return Format_Responce("RegenParam: Rate of Rise Cycles out of range: "+str(Value), error = True)
    elif (Param == '6') & ((Value < 0) | (Value > 80)):
        return Format_Responce("RegenParam: Restart Temperature out of range: "+str(Value), error = True)
    elif (Param == 'A') & ((Value < 0) | (Value > 1)):
        return Format_Responce("RegenParam: Roughing Interlock not 0 or 1: "+str(Value), error = True)
    elif (Param == 'C') & ((Value < 1) | (Value > 3)):
        return Format_Responce("RegenParam: Pumps per Compressor: "+str(Value), error = True)
    elif (Param == 'G') & ((Value < 0) | (Value > 9999)):
        return Format_Responce("RegenParam: Repurge time out of range: "+str(Value), error = True)
    elif (Param == 'z') & ((Value < 0) | (Value > 1)):
        return Format_Responce("RegenParam: Stand by mode not 0 or 1: "+str(Value), error = True)
    else:
        return Send_cmd("P"+str(Param)+str(Value))

# 2.20 • Regeneration Sequence pg:17
def Get_RegenStep(): # Command Ex: "$O>\r"
    return Send_cmd("O")

# 2.21 • 

# 2.22 • Regeneration Step Timer pg:18
def Get_RegenStepTimer(): # Command Ex: "$kZ\r"
    return Send_cmd("k")

# 2.23 • Regeneration Time pg:19
def Get_RegenTime(): # Command Ex: "$aP\r"
    return Send_cmd("a")

# 2.24 • Rough On/Off/Query pg:19
def Get_RoughingValveState(): # Command Ex: "$D?3\r"
    return Send_cmd("D?")
def Open_RoughingValve(): # Command Ex: "$D1d\r"
    return Send_cmd("D1")
def Close_RoughingValve():
    return Send_cmd("D0")

# 2.25 • Rough Valve Interlock pg:20
def Get_RoughingInterlock(): # Command Ex: "$Q?B\r"
    return Send_cmd("Q?")
def Clear_RoughingInterlock(): # Command Ex: "$Q?B\r"
    return Send_cmd("Q")

# 2.26 • Second Stage Temperature pg:20
def Get_SecondStageTemp(): # Command Ex: "$K:\r"
    return Send_cmd("K")

# 2.27 • Second Stage Temperature Control pg:21
def Get_SecondStageTempCTL(): # Command Ex: "$I?:\r"
    return Send_cmd("I?")
def Set_SecondStageTempCTL(temp): # Command Ex: "$I?:\r"
    if (temp < 0) | (temp > 320):
        print('Second stage Temperature out is of range (0-320): {:d}'.format(temp))
        return Format_Responce("Temp out of range: "+str(temp), error = True)
    return Send_cmd("I{0:d}".format(temp))

# 2.28 • Status pg:22
def Get_Status(): # Command Ex: "$S16\r"
    return Send_cmd("S1")

# 2.29 • TC On/Off/Query pg:22
def Get_TcPressureState(): # Command Ex: "$B?3\r"
    return Send_cmd("B?")
def Turn_TcPressureOn():   # Command Ex: "$B1b\r"
    return Send_cmd("B1")
def Turn_TcPressureOff():  # Command Ex: "$B?3\r"
    return Send_cmd("B0")

# 2.30 • Thermocouple Pressure pg:22
def Get_TcPressure(): # Command Ex: "$L=\r"
    return Send_cmd("L")


