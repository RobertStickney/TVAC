#!/usr/bin/env python3.5
# He_Compressor_Interface
import os
import time

from PyCRC_master.PyCRC.CRC16 import CRC16
from Hardware_Drivers.tty_reader import TTY_Reader

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

$Ten: Read selected temperature (n = 1, 2, 3, or 4)
Command with checksum and carriage return = $TE140B8<cr>, $TE241F8<cr>,
$TE38139<cr>, or $TE44378<cr>
Response: $TEn,Tn,<crc-16><cr>


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

    def __init__(self):
        self.crc16 = CRC16()
        self.port = None
        self.port_listener = TTY_Reader(None)
        self.port_listener.daemon = True

    def open_port(self):
        print('Open xuart next.')
        self.port = open('/dev/ttyxuart1', 'r+b', buffering=0)
        print('Opened xuart!')
        self.port_listener.get_fd(self.port)
        self.port_listener.start()
        # self.port_listener.flush_buffer(1.0)

    def flush_port(self):
        self.port_listener.flush_buffer(1.0)

    def close_port(self):
        if not self.port.closed:
            self.port.close()

    def send_cmd(self, command):
        for tries in range(3):
            msg = "${0:s}".format(command)
            # msg1 = "{0:s}{0:04X}\r".format(msg, self.crc(msg))
            print("C:--" + msg.replace('\r', r'\r') + "---")
            self.port.write(msg.encode())
            # TODO: Change to error event print("C:--" + self.GenCmd(Command).replace('\r', r'\r') + "---")
            resp = self.port_listener.read_line(0.5)
            print("R:--" + resp.replace('\r', r'\r') + "---")
            if len(resp) > 0:
                break
            # if self.ResponceGood(resp, command):
            #     if resp[1] == 'A':  # Responce Good!
            #         Data = self.Format_Responce(resp[2:-2])
            #     elif resp[1] == 'B':
            #         Data = self.Format_Responce(resp[2:-2], pwrFail=True)
            #     elif resp[1] == 'E':
            #         Data = self.Format_Responce(resp[2:-2], error=True)
            #     elif resp[1] == 'F':
            #         Data = self.Format_Responce(resp[2:-2], error=True, pwrFail=True)
            #     else:
            #         Data = self.Format_Responce("R--" + resp + "-- unknown", error=True)
            #     break
            #     # TODO: Change to error event print("Try number: " + str(tries))
        else:
            # TODO: Change to error event print("No more tries! Something is wrong!")
            # Data = self.Format_Responce('Timeout!', error=True)
            Data = '----Timeout!-------'
        return Data

    # def ResponceGood(self, Responce):
    #     # TODO: Change to error event print("R:--" + Responce.replace('\r', r'\r') + "---")
    #     if Responce[-1] != '\r':
    #         # TODO: Change to error event print("R:--" + Responce.replace('\r', r'\r') + "--- Missing Carriage Return at the end")
    #         return False
    #     # print("Checksum: '" + Responce[-2] + "' Data: '" + Responce[1:-2] + "' Calc cksum: '" + chr(get_checksum(Responce[1:-2])) + "'")
    #     if Responce[-2] != chr(self.get_checksum(Responce[1:-2])):
    #         # TODO: Change to error event print("R:--" + Responce.replace('\r', r'\r') + "---", "Checksum: " + chr(self.get_checksum(Responce[1:-2])))
    #         return False
    #     if Responce[0] != '$':
    #         # TODO: Change to error event print("R:--" + Responce.replace('\r', r'\r') + "---", "'$' is not the first byte!")
    #         return False
    #     return True  # Yea!! responce seems ok

    def Format_Responce(self, d, error=False, pwrFail=False):  # , d_int = 0, d_float = 0.0);
        return {"Error": error, "PowerFailure": pwrFail, "Response": d}  # , "int"=d_int, "float"=d_float}

    # def get_ParamValues():
    #     # Create Dict of Functions
    #     FunS = {"TEA" : Get_temps,
    #             "Te1" : Get_T1_input,
    #             "Te2" : Get_T2_input,
    #             "Te3" : Get_input,
    #             "PRA" : Get_all_pressures,
    #             "PR1" : Get_selected_pressure,
    #             "ID1" : Get_firmware_ver_and_ETime,
    #             "ON1" : Get_turn_compressor_on,
    #             "OFF" : Get_turn_compressor_off,
    #             "RS1" : Get_Reset,
    #             "CHR" : Get_Cold_Head_Run,
    #             "CHP" : Get_Cold_Head_Pause,
    #             "POF" : Get_Cold_Head_Pause_off}
    #     return RunGetFunctions(FunS)

    # Commands:

    def get_temperatures(self):
        # $TEA: Read all temperatures
        # Command with checksum and carriage return = $TEAA4B9<cr>
        # Response: $TEA,T1,T2,T3,T4,<crc-16><cr>
        resp = self.send_cmd('TEAA4B9\r')
        return resp

    def get_pressure(self):
        # $PRA: Read all pressures
        # Command with checksum and carriage return = $PRA95F7<cr>
        # Response: $PRA,P1,P2,<crc-16><cr>
        # $PRn: Read selected pressure (n = 1 or 2)
        # Command with checksum and carriage return = $PR171F6<cr> or $PR270B6<cr>
        # Response: $PRn,Pn,<crc-16><cr>
        resp = self.send_cmd('PRA95F7\r')
        return resp

    def get_id(self):
        resp = self.send_cmd('ID1D629\r')
        return resp

    def get_status_bits(self):
        resp = int(self.send_cmd('STA3504\r')[4:-5], 16)
        data = {'Config': 'RS-232 Read and Command' if resp & 0x8000 else 'RS-232 Read Only',
                'Op-State': (resp & 0xe00) >> 9,
                'Solenoid ON':       True if resp & 0x100 else False,
                'Pressure Alarm':    True if resp & 0x80 else False,
                'Oil Level Alarm':   True if resp & 0x40 else False,
                'Water Flow Alarm':  True if resp & 0x20 else False,
                'Water Temp Alarm':  True if resp & 0x10 else False,
                'Helium Temp Alarm': True if resp & 0x8 else False,
                'Phase/Fuse Alarm':  True if resp & 0x4 else False,
                'Motor Tempe Alarm': True if resp & 0x2 else False,
                'System ON':         True if resp & 0x1 else False,
                }
        return data

    def set_compressor_on(self):
        resp = self.send_cmd('ON177CF\r')
        return resp

    def set_compressor_off(self):
        resp = self.send_cmd('OFF9188\r')
        return resp


if __name__ == '__main__':
    compressor = Shi_Compressor()
    compressor.open_port()
    compressor.get_temperatures()
    compressor.get_pressure()
    compressor.get_id()
    print(compressor.get_status())
    # compressor.set_compressor_on()
    # print(compressor.get_status())
    # time.sleep(2)
    # compressor.set_compressor_off()
    # print(compressor.get_status())
    # time.sleep(.5)
    # print(compressor.get_status())
    compressor.close_port()
