# -*- coding: utf8 -*-

#
# CRC16Kermit (CRC-CCITT (Kermit)) MODULE
#


from ctypes import c_ushort


class CRC16Kermit(object):
    crc16kermit_tab = []

    # The CRC's are computed using polynomials. Here is the most used
    # coefficient for CRC16 SICK
    crc16Kermit_constant = 0x8408

    def __init__(self):
        # initialize the precalculated tables
        if not len(self.crc16kermit_tab):
            self.init_crc16kermit()

    def calculate(self, input_data=None):
        try:
            is_string = isinstance(input_data, str)
            is_bytes = isinstance(input_data, (bytes, bytearray))

            if not is_string and not is_bytes:
                raise Exception("Please provide a string or a byte sequence "
                                "as argument for calculation.")

            crc_value = 0x0000

            for c in input_data:
                d = ord(c) if is_string else c
                tmp = crc_value ^ d
                crc_value = (crc_value >> 8) ^ self.crc16kermit_tab[(tmp & 0x00ff)]

            # After processing, the one's complement of the CRC is calculated 
            # and two bytes of the CRC are swapped.
            low_byte = (crc_value & 0xff00) >> 8
            high_byte = (crc_value & 0x00ff) << 8
            crc_value = low_byte | high_byte

            return crc_value
        except Exception as e:
            print("EXCEPTION(calculate): {}".format(e))

    def init_crc16kermit(self):
        """the algorithm use tables with precalculated values"""
        for i in range(0, 256):
            crc = c_ushort(i).value
            for j in range(0, 8):
                if crc & 0x0001:
                    crc = c_ushort(crc >> 1).value ^ self.crc16Kermit_constant
                else:
                    crc = c_ushort(crc >> 1).value
            self.crc16kermit_tab.append(crc)
