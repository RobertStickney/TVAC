# -*- coding: utf8 -*-

#
# CRC16SICK MODULE
#

from ctypes import c_ushort


class CRC16SICK(object):
    # The CRC's are computed using polynomials.
    # Here is the most used coefficient for CRC16 SICK
    crc16SICK_constant = 0x8005

    def __init__(self):
        pass

    def calculate(self, input_data=None):
        try:
            is_string = isinstance(input_data, str)
            is_bytes = isinstance(input_data, (bytes, bytearray))

            if not is_string and not is_bytes:
                raise Exception("Please provide a string or a byte sequence \
                    as argument for calculation.")

            crc_value = 0x0000

            for idx, c in enumerate(input_data):
                d = ord(c) if is_string else c
                short_c = 0x00ff & d

                idx_previous = idx - 1
                if idx_previous == -1:
                    prev_c = 0
                else:
                    prev_c = input_data[idx_previous]
                    prev_c = ord(prev_c) if is_string else prev_c

                short_p = (0x00ff & prev_c) << 8

                if crc_value & 0x8000:
                    crc_value = c_ushort(
                        crc_value << 1).value ^ self.crc16SICK_constant
                else:
                    crc_value = c_ushort(crc_value << 1).value

                crc_value &= 0xffff
                crc_value ^= (short_c | short_p)

            # After processing, the one's complement of the CRC is calculated 
            # and the two bytes of the CRC are swapped.
            low_byte = (crc_value & 0xff00) >> 8
            high_byte = (crc_value & 0x00ff) << 8
            crc_value = low_byte | high_byte

            return crc_value
        except Exception as e:
            print("EXCEPTION(calculate): {}".format(e))
