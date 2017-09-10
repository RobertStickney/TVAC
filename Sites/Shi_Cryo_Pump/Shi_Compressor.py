#!/usr/bin/env python3.5
# He_Compressor_Interface
import io
import time
import pyserial

# Runs on serial port at 9600 8 1  Tout >0.7 sec
# $TEA<CR> � read all temps
# $Ten<CR> � read input n = 1 � 4
# $PRA<CR> � Read all pressures. P1 is compressor return in PSI, P2 is N/A (Most variants)
# $PRn<CR> � read selected pressure n-1 or 2
# $STA<CR> � Read Status bits � pretty extensive set of info for this one
# $ID1<CR> � Read firmware ver and Elapsed Time
# $ON1<CR> � turn compressor on
# $OFF<CR> � turn compressor off
# $RS1<CR> � Reset
# $CHR<CR> � Cold Head Run
# $CHP<CR> � Cold Head Pause
# $POF<CR> � Cold Head Pause off

# Any Malformed or Invalid message from host returns $???, 3278<CR>
'''
$TEA: Read all temperatures
Command with checksum and carriage return = $TEAA4B9<cr>
Response: $TEA,T1,T2,T3,T4,<crc-16><cr>

$Ten: Read selected temperature (n = 1, 2, 3, or 4)
Command with checksum and carriage return = $TE140B8<cr>, $TE241F8<cr>,
$TE38139<cr>, or $TE44378<cr>
Response: $TEn,Tn,<crc-16><cr>

$PRA: Read all pressures
Command with checksum and carriage return = $PRA95F7<cr>
Response: $PRA,P1,P2,<crc-16><cr>

$PRn: Read selected pressure (n = 1 or 2)
Command with checksum and carriage return = $PR171F6<cr> or $PR270B6<cr>
Response: $PRn,Pn,<crc-16><cr>

$STA: Read Status bits
Command with checksum and carriage return = $STA3504<cr>
Response: $STA,status bits,<crc-16><cr>
'''
# $ID1: Read firmware version and elapsed operating hours
# Command with checksum and carriage return = $ID1D629<cr>
# Response: $ID1,version number,elapsed hours,reserved number,<crc-16><cr>

# $ON1: On
# Command with checksum and carriage return = $ON177CF<cr>
# Response: $ON1,<crc-16><cr>

# $OFF: Off
# Command with checksum and carriage return = $OFF9188<cr>
# Response: $OFF,<crc-16><cr>

# $RS1: Reset
# Command with checksum and carriage return = $RS12156<cr>
# Response: $RS1,<crc-16><cr>

# $CHR: Cold Head Run
# Command with checksum and carriage return = $CHRFD4C<cr>
# Response: $CHR,<crc-16><cr>

# $CHP: Cold Head Pause
# Command with checksum and carriage return = $CHP3CCD<cr>
# Response: $CHP,<crc-16><cr>

# $POF: Cold Head Pause Off
# Command with checksum and carriage return = $POF07BF<cr>
# Response: $POF,<crc-16><cr>

# INVALID: Malformed or invalid message from host computer.
# Response: $???,<crc-16><cr> (crc-16 = 3278)

# The status bits are contained in a four character field that is the ASCII hex equivalent of
# a 16 bit word. For example, a status bit field of "0301" is equivalent to a binary
# '0000001100000001". The left most character is the MSbit. Bits are defined as follows:
# Bit 15 - 0 = Configuration 1. 1 = Configuration 2. Note that in Configuration 2 only the
# "read" RS232 commands are functional. Note: Refer to compressor operating
# manual for explanation and setting of configuration 1 or 2.
# Bit 14 - spare.
# Bit 13 - spare.
# Bit 12 - spare.

# Bit 11 - MSbit of state number.
# Bit 10 - Middlebit of state number.
# Bit 9 - LSbit of state number. The state number reflects the state of operation:
# 7 - Oil Fault Off
# 6 - Fault Off
# 5 - Cold Head Pause
# 4 - Cold Head Run
# 3 - Remote On
# 2 - Remote Off (temporary state not normally returned)
# 1 - Local On
# 0 - Local Off


# Lower 9 bits of STATUS Word:
# Bit 0 - 1 = System ON. 0 = System OFF.
# Bit 1 - 1 = Motor Temperature alarm. 0 = no alarm.
# Bit 2 - 1 = Phase Sequence/Fuse alarm. 0 = no alarm.
# Bit 3 - 1 = Helium Temperature alarm. 0 = no alarm.
# Bit 4 - 1 = Water Temperature alarm. 0 = no alarm.
# Bit 5 - 1 = Water Flow alarm. 0 = no alarm.
# Bit 6 - 1 = Oil Level alarm. 0 = no alarm.
# Bit 7 - 1 = Pressure alarm. 0 = no alarm.
# Bit 8 - 1 = Solenoid on. 0 = Solenoid off.

#Status = concantenation of 4 Bytes
Stat0 = Status and 1
Stat1 = Status and 2
Stat2 = Status and 3
Stat3 = Status and 4
Stat4 = Status and 5
Stat5 = Status and 6
Stat6 = Status and 7
Stat7 = Status and 8
Stat8 = Status and 9
Stat9 = Status and A
Stat10 = Status and B
Stat11 = Status and C
Stat15 = Status and F
Stat_Comb = Stat9 orStat10 or Stat11

if stat0 = 1 then System = ON
if stat0 = 0 then System = OFF

if stat1 = 1 then Motor_Temperature_alarm = ON
if stat1 = 0 then Motor_Temperature_alarm = OFF

if stat2 = 1 then Phase_Sequence/Fuse_alarm = ON
if stat2 = 0 then Phase_Sequence/Fuse_alarm = OFF

if stat3 = 1 then Helium_Temperature_alarm = ON
if stat3 = 0 then Helium_Temperature_alarm = OFF

if stat4 = 1 then Water_Temperature_alarm = ON
if stat4 = 0 then Water_Temperature_alarm = OFF

if stat5 = 1 then Water_Flow_alarm = ON
if stat5 = 0 then Water_Flow_alarm = OFF

if stat6 = 1 then Oil_Level_alarm = ON
if stat6 = 0 then Oil_Level-alarm = OFF

if stat7 = 1 then Pressure_alarm = ON
if stat7 = 0 then Pressure_alarm = OFF

if stat8 = 1 then Solenoid = ON
if stat8 = 0 then Solenoid = OFF

# Decode Status Word - 4 Bytes
if Stat_Comb  = 0 then Local_Off
     elif Stat_Comb = 1 then Local_On
     elif Stat_Comb = 2 then Remote_Off
     elif Stat_Comb = 3 then Remote_On
     elif Stat_Comb = 4 then Cold_Head_Run
     elif Stat_Comb = 5 then Cold_Head_Pause
     elif Stat_Comb = 6 then Fault_Off
     elif Stat_Comb = 7 then Oil_Fault_Off

# Bit 15 - 0 = Configuration 1
if stat15 = 1 then Configuration = 2 
if stat15 = 0 then Configuration = 1

# Example response $STA,0301,2ED1<cr> corresponds to binary 0000001100000001 or :
# Local ON, solenoid ON, System ON, and no alarms.



def HeCompressorOpen(Command):
    He_Comp = open('/dev/ttyxuart1', 'r+b', buffering=0)
    He_Comp.write(Command.encode()'\r)
    time.sleep(0.760)
    temp = HE_Comp.read(113)
    print("R:--" + temp.decode().replace('\r', r'\r') + "---")
    return temp.decode()

def Compressor_GenCmdRead( Parm=349): #Cmd syntax see page #16 of MPT200 Operating instructions
    return Pfeiffer_applyChecksum("{:03d}00{:03d}02=?".format( Parm))
	
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

# 2.4 � Duty Cycle pg:8
def Get_DutyCycle(): # Command Ex: "$XOI??_\r"
    #return (int(Send_cmd("XOI??"))/23) * 100 #check for int
    return Send_cmd("XOI??")

# 2.5 � Elapsed Time pg:8
def Get_ElapsedTime(): # Command Ex: "$Y?J\r"
    return Send_cmd("Y?")
 
# Commands:

    return RunGetFunctions(FunS)

def get_Status():
    # Create Dict of Functions 
    FunS = {"Status"            : Get_Status,
	return get_Status(Funs)

def get_ParamValues():
    # Create Dict of Functions             
    FunS = {"TEA" : Get_temps,
            "Te1" : Get_T1_input,
            "Te2" : Get_T2_input,
            "Te3" : Get_input,
            "PRA" : Get_all_pressures, 
            "PR1" : Get_selected_pressure,
            "ID1" : Get_firmware_ver_and_ETime,
            "ON1" : Get_turn_compressor_on,
            "OFF" : Get_turn_compressor_off,
            "RS1" : Get_Reset,
            "CHR" : Get_Cold_Head_Run,
            "CHP" : Get_Cold_Head_Pause,
            "POF" : Get_Cold_Head_Pause_off}
    return RunGetFunctions(FunS)