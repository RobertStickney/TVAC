# !/usr/bin/env python3

import time
import os
import sys
import mmap


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
            print('Board Model #: 0x{0:x}; Byte 0: 0x{1:x}'.format(int.from_bytes(self.syscon.read(2), sys.byteorder),
                                                                   b1))
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

    def DIO_Read4(self, cardNum=1, DigIn=True):
        if DigIn:  # read to digital inputs
            if cardNum == 2:
                addr = self.Dio2_Addr(self.DioInBaseAddr)
            else:
                addr = self.Dio1_Addr(self.DioInBaseAddr)
        else:  # read to digital outputs
            if cardNum == 2:
                addr = self.Dio2_Addr(self.DioOutBaseAddr)
            else:
                addr = self.Dio1_Addr(self.DioOutBaseAddr)
        self.pc104.seek(addr)
        return [self.pc104.read_byte(),
                self.pc104.read_byte(),
                self.pc104.read_byte(),
                self.pc104.read_byte()]

    def __DIO_Read_byte__(self, address):
        self.pc104.seek(address)
        return self.pc104.read_byte()

    def __DIO_Write_byte__(self, address, b):
        self.pc104.seek(address)
        self.pc104.write_byte(b)

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


# Command lines testing of driver
if __name__ == '__main__':
    ts = TS_Registers()
    ts.open_Registers()
    # ts.test_mmap()

    if (len(sys.argv) > 2):
        if sys.argv[1] == 'di':
            if sys.argv[2] == '2':
                addr = ts.Dio2_Addr(ts.DioInBaseAddr)
            else:
                addr = ts.Dio1_Addr(ts.DioInBaseAddr)
            b = ts.DIO_Read(sys.argv[2])
            print(type(b))
            print("DIO address: {:x} bytes: 0x{:02x} {:02x} {:02x} {:02x}".format(addr, b[3], b[2], b[1], b[1]))
        elif sys.argv[1] == 'do':
            if (len(sys.argv) > 4):
                if sys.argv[3] == 'set':  # cardNum, pinNum,    SetBit
                    ts.DIO_Write_Pin(sys.argv[2], sys.argv[4], True)
                elif sys.argv[3] == 'clear':
                    ts.DIO_Write_Pin(sys.argv[2], sys.argv[4], False)
    ts.close()
