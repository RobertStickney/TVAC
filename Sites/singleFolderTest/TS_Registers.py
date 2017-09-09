# !/usr/bin/env python3

import time
import os
import sys
import mmap

# from HouseKeeping.globalVars import debugPrint
from globalVars import debugPrint

class TS_Registers():
    def __init__(self):
        self.fp = None
        self.syscon = None
        self.pc104 = None
        self.SysconAddr = 0x80004000
        self.Pc104Addr = 0x81008000
        self.DioOutBaseAddr = 0x4
        self.DioInBaseAddr = 0x8

    def Dio1_Addr(self, offset):  # JP1 off, JP2 off
        return 0x100 + (offset & 0xf)

    def Dio2_Addr(self, offset):  # JP1 on, JP2 off
        return 0x110 + (offset & 0xf)

    def Adc16Addr(self, offset):  # JP1 off, JP2 on
        return 0x140 + (offset & 0x1f)

    def open_Registers(self, printID=True):  # note sys.byteorder = 'little' on TS-7250-V2
        self.fp = os.open('/dev/mem', os.O_RDWR | os.O_NONBLOCK | os.O_SYNC)
        self.syscon = mmap.mmap(self.fp, 4096, offset=self.SysconAddr)
        self.syscon.seek(0)
        b1 = self.syscon.read_byte()
        self.syscon.seek(0)
        if printID:
            print('Board Model #: 0x{0:x}; Byte 0: 0x{1:x}'.format(int.from_bytes(self.syscon.read(2), sys.byteorder), b1))
        self.pc104 = mmap.mmap(self.fp, 4096, offset=self.Pc104Addr)
        self.enPc104()
        if printID:
            self.pc104.seek(self.Dio1_Addr(0))
            print("1st DIO64 Board ID: 0x{:02x} 0x{:02x}".format(self.pc104.read_byte(), self.pc104.read_byte()))
            self.pc104.seek(self.Dio2_Addr(0))
            print("2nd DIO64 Board ID: 0x{:02x} 0x{:02x}".format(self.pc104.read_byte(), self.pc104.read_byte()))
            self.pc104.seek(self.Adc16Addr(0))
            print("ADC-16 Board ID: 0x{:02x} 0x{:02x} \n".format(self.pc104.read_byte(), self.pc104.read_byte()))

    def close(self):
        self.pc104.close()
        self.syscon.close()
        os.close(self.fp)

    def bits_clear(self, mm, pos, byte):
        mm.seek(pos)
        b = mm.read_byte()
        mm.seek(pos)
        mm.write_byte(b & ~(byte & 0xFF))

    def bits_set(self, mm, pos, byte):
        mm.seek(pos)
        b = mm.read_byte()
        mm.seek(pos)
        mm.write_byte(b | (byte & 0xFF))

    def LED_Green_on(self):
        self.bits_set(self.syscon, 0x13, 0x08)

    def LED_Green_off(self):
        self.bits_clear(self.syscon, 0x13, 0x08)

    def LED_Red_on(self):
        self.bits_set(self.syscon, 0x13, 0x10)

    def LED_Red_off(self):
        self.bits_clear(self.syscon, 0x13, 0x10)

    def setEVGPIO(self, pinNum):
        if pinNum < 64:  # EVGPIO 0-63
            self.syscon.seek(0x36)
        else:  # EVGPIO 64-127
            self.syscon.seek(0x3a)
        self.syscon.write_byte(0x80 | (pinNum & 63))
        self.syscon.write_byte(0)

    def clearEVGPIO(self, pinNum):
        if pinNum < 64:  # EVGPIO 0-63
            self.syscon.seek(0x36)
        else:  # EVGPIO 64-127
            self.syscon.seek(0x3a)
        self.syscon.write_byte(pinNum & 63)
        self.syscon.write_byte(0)

    def test_mmap(self):
        sleeptime = 0.1
        self.LED_Red_off()
        self.LED_Green_off()
        for i in range(10):
            self.LED_Red_on()
            time.sleep(sleeptime)
            self.LED_Green_on()
            time.sleep(sleeptime)
            self.LED_Red_off()
            time.sleep(sleeptime)
            self.LED_Green_off()
            time.sleep(sleeptime)
        self.close()

    def enPc104(self):
        self.setEVGPIO(0)
        self.setEVGPIO(1)
        self.setEVGPIO(2)
        self.setEVGPIO(3)
        self.clearEVGPIO(7)

    def __DIO_Read_byte__(self, address):
        self.pc104.seek(address)
        return self.pc104.read_byte()

    def __DIO_Write_byte__(self, address, b):
        self.pc104.seek(address)
        self.pc104.write_byte(b)

    def dio_read4(self, cardNum=1, DigIn=True):
        if cardNum == 2:
            if DigIn:  # read digital inputs on card 2
                addr = self.Dio2_Addr(self.DioInBaseAddr)
            else:  # read digital outputs on card 2
                addr = self.Dio2_Addr(self.DioOutBaseAddr)
            key = ['C2 B0', 'C2 B1', 'C2 B2', 'C2 B3']
        else:
            if DigIn:  # read digital inputs on card 1
                addr = self.Dio1_Addr(self.DioInBaseAddr)
            else:  # read digital outputs on card 1
                addr = self.Dio1_Addr(self.DioOutBaseAddr)
            key = ['C1 B0', 'C1 B1', 'C1 B2', 'C1 B3']
        self.pc104.seek(addr)
        return {key[0]: self.pc104.read_byte(),
                key[1]: self.pc104.read_byte(),
                key[2]: self.pc104.read_byte(),
                key[3]: self.pc104.read_byte()}

    def do_write4(self, bytes, cardNum = 1):
        if cardNum == 2:
            addr = self.Dio2_Addr(self.DioOutBaseAddr)
        else:
            addr = self.Dio1_Addr(self.DioOutBaseAddr)
        self.pc104.seek(addr)
        self.pc104.write_byte(bytes[0])
        self.pc104.write_byte(bytes[1])
        self.pc104.write_byte(bytes[2])
        self.pc104.write_byte(bytes[3])

    #      cardNum = 1|2;  pinNum Starts at 1
    def DIO_Write_Pin(self, cardNum, pinNum, setBit):
        pinNum = 31 & int(pinNum - 1)
        addr = (pinNum >> 3) + self.DioOutBaseAddr
        if cardNum == 2:
            addr = self.Dio2_Addr(addr)
        else:  # assume cardNum = 1
            addr = self.Dio1_Addr(addr)
        b = self.__DIO_Read_byte__(addr)
        print("DIO address: {:x}; byte: {:02x}".format(addr, b))
        mask = 0x01 << (7 & pinNum)
        if setBit:
            b |= mask
        else:  # clearBit
            b &= ~mask
        self.__DIO_Write_byte__(addr, b)
        print("Write byte: 0x{:x}".format(b))

    def dac_write(self, value, channel):
        self.pc104.seek(self.Adc16Addr(0x0E))
        self.pc104.write_byte(value & 0xFF)
        self.pc104.write_byte(((channel & 0x03) << 6) | 0x30 | ((value & 0xF00)>>8))

    def start_adc(self,
                  sys_com = 1,          # 1 = Start ADC conversion state machine
                  num_chan = 7,         # Range: 0-7; Acquire Channel 0 to (num_chan*2)+1
                  adc_delay = 400000,   # adc clock 32,000,000Hz/400,000 = 80Hz; 80Hz/8(ch pairs) = 10Hz; 1/10Hz = 0.1s
                  single_ended = 1,     # Single ended = 1; Differential = 0
                  input_range = 1,      # Input Range: 0 = -5V to +5V; 1 = 0V to +5V; 2 = -10V to +10V; 3 = 0V to +10V
                  ext_trig = 0,         # 1 = Start ADC with sys_com; 0 = Start ADC when digital in
                  fifo_int_trig = 256,  # Fifo level to trigger interrupt
                  fifo_en_int = 0):     # 1 = Enable fifo interrupt
        self.pc104.seek(self.Adc16Addr(0x08))  # ADCSTAT
        self.pc104.write_byte(((fifo_int_trig & 0x3) << 6) | (fifo_en_int & 0x01))
        self.pc104.write_byte((fifo_int_trig & 0x3fc) >> 2)

        self.pc104.seek(self.Adc16Addr(0x04))  # ADCDLY_MSB
        self.pc104.write_byte((adc_delay & 0xFF0000) >> 16)

        self.pc104.seek(self.Adc16Addr(0x06))  # ADCDLY_LSB
        self.pc104.write_byte(adc_delay & 0xFF)
        self.pc104.write_byte((adc_delay & 0xFF00) >> 8)

        self.pc104.seek(self.Adc16Addr(0x03))  # ADCCFG_MSB
        self.pc104.write_byte(((ext_trig & 0x01) << 1) | (single_ended & 0x01))

        self.pc104.seek(self.Adc16Addr(0x02))  # ADCCFG_LSB Writing to this byte resets the adc state machine.
        self.pc104.write_byte(((input_range & 0x03) << 6) |
                              ((single_ended & 0x01) << 5) |
                              ((num_chan & 0x07) << 1) |
                              (sys_com & 0x01))

    def adc_fifo_status(self):
        self.pc104.seek(self.Adc16Addr(0x08))  # ADCSTAT
        b1 = self.pc104.read_byte()
        b2 = self.pc104.read_byte()
        debugPrint(4, "ADC FIFO Status: 0x{:x} 0x{:x}".format(b1,b2))
        return ((b1 & 0x3e) >> 1,  # FFHEAD: Channel on head of fifo. It increments to (num_chan*2)+1 then wraps to 0
                ((b2 & 0xff) << 2) | ((b1 & 0xC0) >> 6))  # Number of elements in fifo

    def adc_fifo_read(self):  # channel #'s for the values returned is FFHEAD
        self.pc104.seek(self.Adc16Addr(0x1A))  # ADCFIFO_LSB
        b = self.pc104.read_byte()                # read ADCFIFO_LSB
        return (self.pc104.read_byte() << 8) | b  # read ADCFIFO_MSB

# Command lines testing of driver
if __name__ == '__main__':
    ts = TS_Registers()
    ts.open_Registers()
    # ts.test_mmap()

    if (len(sys.argv) > 2):
        if sys.argv[1] == 'di':
            if sys.argv[2] == '2':
                address = ts.Dio2_Addr(ts.DioInBaseAddr)
            else:
                address = ts.Dio1_Addr(ts.DioInBaseAddr)
            #b = ts.DIO_Read(sys.argv[2])
            print(type(b))
            print("DIO address: {:x} bytes: 0x{:02x} {:02x} {:02x} {:02x}".format(address, b[3], b[2], b[1], b[1]))
        elif sys.argv[1] == 'do':
            if (len(sys.argv) > 4):
                if sys.argv[3] == 'set':  # cardNum, pinNum,    SetBit
                    ts.DIO_Write_Pin(sys.argv[2], sys.argv[4], True)
                elif sys.argv[3] == 'clear':
                    ts.DIO_Write_Pin(sys.argv[2], sys.argv[4], False)
    ts.close()
