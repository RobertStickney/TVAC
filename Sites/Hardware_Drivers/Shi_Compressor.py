#!/usr/bin/env python3.5

from PyCRC_master.PyCRC.CRC16 import CRC16
from Hardware_Drivers.tty_reader import TTY_Reader

from Logging.Logging import Logging


class ShiCompressor:

    def __init__(self):
        self.crc = CRC16(modbus_flag=True).calculate
        self.port = None
        self.port_listener = TTY_Reader(None)
        self.port_listener.daemon = True

    def open_port(self):
        self.port = open('/dev/ttyxuart1', 'r+b', buffering=0)
        self.port_listener.get_fd(self.port)
        self.port_listener.start()
        self.port_listener.flush_buffer(1.0)

    def flush_port(self):
        self.port_listener.flush_buffer(1.0)

    def close_port(self):
        if not self.port.closed:
            self.port.close()

    def send_cmd(self, command):
        for tries in range(3):
            msg = "${:s}".format(command)
            msg1 = "{:s}{:04X}\r".format(msg, self.crc(msg))
            print("C:--" + msg1.replace('\r', r'\r') + "---")  # TODO: Remove print and msg1
            self.port.write(msg1.encode())
            # TODO: Change to error event print("C:--" + self.GenCmd(Command).replace('\r', r'\r') + "---")
            resp = self.port_listener.read_line(0.7).strip()
            print("R:--" + resp.replace('\r', r'\r') + "---")
            if self.ResponceGood(resp, command):
                data = resp.split(',')
                if len(data) >= 2:
                    break
            Logging.logEvent("Debug", "Status Update",
                             {"message": "SHI Compressor send_cmd try #{:d}".format(tries),
                              "level": 1})
        else:
            Logging.logEvent("Debug", "Status Update",
                             {"message": "SHI Compressor send_cmd Failed.",
                              "level": 1})
            raise Exception('SHI Compressor send_cmd Failed.')
        return data[1:-1]

    def ResponceGood(self, Responce, cmd):
        # TODO: Change to error event print("R:--" + Responce.replace('\r', r'\r') + "---")
        # print("Checksum: '" + Responce[-2] + "' Data: '" + Responce[1:-2] + "' Calc cksum: '" + chr(get_checksum(Responce[1:-2])) + "'")
        # TODO: Change to error event print("R:--" + Responce.replace('\r', r'\r') + "---")
        if len(Responce) < 4:
            # TODO: Change to error event print("R:--" + Responce.replace('\r', r'\r') + "--- Missing Carriage Return at the end")
            return False
        if Responce[0] != '$':
            # TODO: Change to error event print("R:--" + Responce.replace('\r', r'\r') + "---", "'$' is not the first byte!")
            return False
        if not cmd in Responce:
            # TODO: Change to error event print("R:--" + Responce.replace('\r', r'\r') + "---", "'$' is not the first byte!")
            return False
        if Responce[-4:] != '{:04X}'.format(self.crc(Responce[:-4])):
            # TODO: Change to error event print("R:--" + Responce.replace('\r', r'\r') + "---", "Checksum: " + chr(self.crc(Responce(:-4])))
            return False
        return True  # Yea!! responce seems ok

    # Commands:

    def get_temperatures(self):
        # $TEA: Read all temperatures
        # Command with checksum and carriage return = $TEAA4B9<cr>
        # Response: $TEA,T1,T2,T3,T4,<crc-16><cr>
        resp = self.send_cmd('TEA')
        return {'Helium Discharge Temperature': int(resp[0]),
                'Water Outlet Temperature': int(resp[1]),
                'Water Inlet Temperature': int(resp[2]),
                }

    def get_pressure(self):
        # $PRn: Read selected pressure (n = 1 or 2)
        # Command with checksum and carriage return = $PR171F6<cr> or $PR270B6<cr>
        # Response: $PRn,Pn,<crc-16><cr>  Pn is the pressure in psig
        resp = self.send_cmd('PR1')
        return {'Helium Return Pressure': int(resp[0])}

    def get_id(self):
        resp = self.send_cmd('ID1')
        return {'Firmware Version': resp[0],
                'Operating Hours Elapsed': float(resp[1]),
                }

    def get_status_bits(self):
        resp = int(self.send_cmd('STA').split(',')[1], 16)
        return {'RS-232 Config': 'Read Only' if resp & 0x8000 else 'Command and Read',
                'Solenoid ON':       True if resp & 0x100 else False,
                'Pressure Alarm':    True if resp & 0x80 else False,
                'Oil Level Alarm':   True if resp & 0x40 else False,
                'Water Flow Alarm':  True if resp & 0x20 else False,
                'Water Temp Alarm':  True if resp & 0x10 else False,
                'Helium Temp Alarm': True if resp & 0x8 else False,
                'Phase/Fuse Alarm':  True if resp & 0x4 else False,
                'Motor Temp Alarm': True if resp & 0x2 else False,
                'System ON':         True if resp & 0x1 else False,
                'Op-State':  {0: '0 - Local Off',
                              1: '1 - Local ON',
                              2: '2 - Remote Off',
                              3: '3 - Remote ON',
                              4: '4 - Cold Head Run',
                              5: '5 - Cold Head Pause',
                              6: '6 - Fault Off',
                              7: '7 - Oil Fault Off'}[(resp & 0xe00) >> 9]}

    def set_compressor_on(self):
        resp = self.send_cmd('ON1')
        return resp

    def set_compressor_off(self):
        resp = self.send_cmd('OFF')
        return resp

    def set_reset(self):
        resp = self.send_cmd('RS1')
        return resp


if __name__ == '__main__':
    pass
