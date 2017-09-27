#!/usr/bin/env python3.5
# He_Compressor_Interface
import os
import time

from PyCRC_master.PyCRC.CRC16 import CRC16

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
# Stat0 = Status and 1
# Stat1 = Status and 2
# Stat2 = Status and 3
# Stat3 = Status and 4
# Stat4 = Status and 5
# Stat5 = Status and 6
# Stat6 = Status and 7
# Stat7 = Status and 8
# Stat8 = Status and 9
# Stat9 = Status and A
# Stat10 = Status and B
# Stat11 = Status and C
# Stat15 = Status and F
# Stat_Comb = Stat9 orStat10 or Stat11
#
# if stat0 = 1 then System = ON
# if stat0 = 0 then System = OFF
#
# if stat1 = 1 then Motor_Temperature_alarm = ON
# if stat1 = 0 then Motor_Temperature_alarm = OFF
#
# if stat2 = 1 then Phase_Sequence/Fuse_alarm = ON
# if stat2 = 0 then Phase_Sequence/Fuse_alarm = OFF
#
# if stat3 = 1 then Helium_Temperature_alarm = ON
# if stat3 = 0 then Helium_Temperature_alarm = OFF
#
# if stat4 = 1 then Water_Temperature_alarm = ON
# if stat4 = 0 then Water_Temperature_alarm = OFF
#
# if stat5 = 1 then Water_Flow_alarm = ON
# if stat5 = 0 then Water_Flow_alarm = OFF
#
# if stat6 = 1 then Oil_Level_alarm = ON
# if stat6 = 0 then Oil_Level-alarm = OFF
#
# if stat7 = 1 then Pressure_alarm = ON
# if stat7 = 0 then Pressure_alarm = OFF
#
# if stat8 = 1 then Solenoid = ON
# if stat8 = 0 then Solenoid = OFF
#
# # Decode Status Word - 4 Bytes
# if Stat_Comb  = 0 then Local_Off
#      elif Stat_Comb = 1 then Local_On
#      elif Stat_Comb = 2 then Remote_Off
#      elif Stat_Comb = 3 then Remote_On
#      elif Stat_Comb = 4 then Cold_Head_Run
#      elif Stat_Comb = 5 then Cold_Head_Pause
#      elif Stat_Comb = 6 then Fault_Off
#      elif Stat_Comb = 7 then Oil_Fault_Off
#
# # Bit 15 - 0 = Configuration 1
# if stat15 = 1 then Configuration = 2
# if stat15 = 0 then Configuration = 1

# Example response $STA,0301,2ED1<cr> corresponds to binary 0000001100000001 or :
# Local ON, solenoid ON, System ON, and no alarms.

class Shi_Compressor:

    def Send_cmd(self, Command):
        MCC = open('/dev/ttyxuart1  ', 'r+b', buffering=0)
        for tries in range(3):
            MCC.write(self.GenCmd(Command).encode())
            time.sleep(0.10 * (tries + 1))
            # TODO: Change to error event print("C:--" + self.GenCmd(Command).replace('\r', r'\r') + "---")
            resp = MCC.read(64).decode()
            if self.ResponceGood(resp):
                if resp[1] == 'A':  # Responce Good!
                    Data = self.Format_Responce(resp[2:-2])
                elif resp[1] == 'B':
                    Data = self.Format_Responce(resp[2:-2], pwrFail=True)
                elif resp[1] == 'E':
                    Data = self.Format_Responce(resp[2:-2], error=True)
                elif resp[1] == 'F':
                    Data = self.Format_Responce(resp[2:-2], error=True, pwrFail=True)
                else:
                    Data = self.Format_Responce("R--" + resp + "-- unknown", error=True)
                break
                # TODO: Change to error event print("Try number: " + str(tries))
        else:
            # TODO: Change to error event print("No more tries! Something is wrong!")
            Data = self.Format_Responce('Timeout!', error=True)
        MCC.close()
        return Data

    def get_checksum(self, cmd):  # append the sum of the string's bytes mod 256 + '\r'
        d = sum(cmd.encode())
        #       0x30 + ( (d2 to d6) or (d0 xor d6) or ((d1 xor d7) shift to d2)
        return 0x30 + ((d & 0x3c) |
                       ((d & 0x01) ^ ((d & 0x40) >> 6)) |  # (d0 xor d6)
                       ((d & 0x02) ^ ((d & 0x80) >> 6)))  # (d1 xor d7)

    def GenCmd(self, cmd, data=''):  # Cmd syntax see page MCC Programing Guide
        msg = "${0}{1}".format(cmd, data)
        return "{0}{1:c}\r".format(msg, self.get_checksum(msg))

    def ResponceGood(self, Responce):
        # TODO: Change to error event print("R:--" + Responce.replace('\r', r'\r') + "---")
        if Responce[-1] != '\r':
            # TODO: Change to error event print("R:--" + Responce.replace('\r', r'\r') + "--- Missing Carriage Return at the end")
            return False
        # print("Checksum: '" + Responce[-2] + "' Data: '" + Responce[1:-2] + "' Calc cksum: '" + chr(get_checksum(Responce[1:-2])) + "'")
        if Responce[-2] != chr(self.get_checksum(Responce[1:-2])):
            # TODO: Change to error event print("R:--" + Responce.replace('\r', r'\r') + "---", "Checksum: " + chr(self.get_checksum(Responce[1:-2])))
            return False
        if Responce[0] != '$':
            # TODO: Change to error event print("R:--" + Responce.replace('\r', r'\r') + "---", "'$' is not the first byte!")
            return False
        return True  # Yea!! responce seems ok

    def Format_Responce(self, d, error=False, pwrFail=False):  # , d_int = 0, d_float = 0.0);
        return {"Error": error, "PowerFailure": pwrFail, "Response": d}  # , "int"=d_int, "float"=d_float}

    def get_Status(self):
        # Create Dict of Functions
        FunS = {"Duty Cycle": self.Get_DutyCycle,  # 2.4 ------------------- Ex: "$XOI??_\r"
                "Stage 1 Temp": self.Get_FirstStageTemp,  # 2.8 ------------ Ex: "$J;\r"
                "Cryo Pump Ready State": self.Get_CryoPumpRdyState,  # 2.14  Ex: "$A?2\r"
                "Purge Valve State": self.Get_PurgeValveState,  # 2.15 ----- Ex: "$E?6\r"
                "Regen Error": self.Get_RegenError,  # 2.18 ---------------- Ex: "$eT\r"
                "Regen Step": self.Get_RegenStep,  # 2.20 ------------------ Ex: "$O>\r"
                "Roughing Valve State": self.Get_RoughingValveState,  # 2.24 Ex: "$D?3\r"
                "Roughing Interlock": self.Get_RoughingInterlock,  # 2.25 -- Ex: "$Q?B\r"
                "Stage 2 Temp": self.Get_SecondStageTemp,  # 2.26 ---------- Ex: "$K:\r"
                "Status": self.Get_Status,  # 2.28 ------------------------- Ex: "$S16\r"
                "Tc Pressure": self.Get_TcPressure}  # 2.30 ---------------- Ex: "$L=\r"
        return self.run_GetFunctions(FunS)

    def get_ParamValues(self):
        # Create Dict of Functions
        FunS = {"Elapsed Time": self.Get_ElapsedTime,  # 2.5 -------------------------- Ex: "$Y?J\r"
                "Failed Rate Of Rise Cycles": self.Get_Failed_RateOfRise_Cycles,  # 2.6 Ex: "$m\\r"
                "Failed Repurge Cycles": self.Get_FailedRepurgeCycles,  # 2.7 --------- Ex: "$l]\r"
                "First Stage Temp CTL": self.Get_FirstStageTempCTL,  # 2.9 ------------ Ex: "$H?5\r"
                "Last Rate Of Rise Value": self.Get_LastRateOfRiseValue,  # 2.10 ------ Ex: "$n_\r"
                "MCC Version": self.Get_ModuleVersion,  # 2.11 ------------------------ Ex: "$@1\r"
                "Power Failure Recovery": self.Get_PowerFailureRecovery,  # 2.12 ------ Ex: "$i?H\r"
                "Power Failure Recovery Status": self.Get_PowerFailureRecoveryStatus,  # 2.13 Ex: "$t?a\r"
                "Regen Cycles": self.Get_RegenCycles,  # 2.17 - Ex: "$Z?K\r"
                "Regen Param_0": self.Get_RegenParam_0,  # 2.19 Ex: "P0?"
                "Regen Param_1": self.Get_RegenParam_1,  # 2.19 Ex: "P1?"
                "Regen Param_2": self.Get_RegenParam_2,  # 2.19 Ex: "P2?"
                "Regen Param_3": self.Get_RegenParam_3,  # 2.19 Ex: "P3?"
                "Regen Param_4": self.Get_RegenParam_4,  # 2.19 Ex: "P4?"
                "Regen Param_5": self.Get_RegenParam_5,  # 2.19 Ex: "P5?"
                "Regen Param_6": self.Get_RegenParam_6,  # 2.19 Ex: "P6?"
                "Regen Param_A": self.Get_RegenParam_A,  # 2.19 Ex: "PA?"
                "Regen Param_C": self.Get_RegenParam_C,  # 2.19 Ex: "PC?"
                "Regen Param_G": self.Get_RegenParam_G,  # 2.19 Ex: "PG?"
                "Regen Param_z": self.Get_RegenParam_z,  # 2.19 Ex: "Pz?"
                "Regen Start Delay": self.Get_RegenStartDelay,  # 2.21 ------ Ex: "$j?[\r"
                "Regen Step Timer": self.Get_RegenStepTimer,  # 2.22 -------- Ex: "$kZ\r"
                "Regen Time": self.Get_RegenTime,  # 2.23 ------------------- Ex: "$aP\r"
                "Second Stage Temp CTL": self.Get_SecondStageTempCTL,  # 2.27 Ex: "$I?:\r"
                "Tc Pressure State": self.Get_TcPressureState}  # 2.29 ------ Ex: "$B?3\r"
        return self.run_GetFunctions(FunS)

    def run_GetFunctions(self, Functions):
        er = False
        pf = False
        vals = {}
        for key in Functions.keys():
            val = Functions[key]()
            er |= val['Error']
            pf |= val['PowerFailure']
            if 'Data' in val:
                vals[key] = val['Data']
            else:
                vals[key] = val['Response']
        return self.Format_Responce(vals, er, pf)

    # MCC Programmers References Guide Rev C
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

if __name__ == '__main__':
    pass