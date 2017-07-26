#!/usr/bin/env python3

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

	def Dio1_Addr(self, offset): # JP1 off, JP2 off
		return 0x100 + (offset & 0xf)

	def Dio2_Addr(self, offset): # JP1 on, JP2 off
		return 0x110 + (offset & 0xf)

	def Adc16Addr(self, offset): # JP1 off, JP2 on
		return 0x140 + (offset & 0x1f)


	def open_Registers(self): # note sys.byteorder = 'little' on TS-7250-V2
		self.fp = os.open('/dev/mem', os.O_RDWR|os.O_NONBLOCK|os.O_SYNC)
		self.syscon = mmap.mmap(self.fp, 4096, offset=self.SysconAddr)
		self.syscon.seek(0)
		b1 = self.syscon.read_byte()
		self.syscon.seek(0)
		print('Board Model #: 0x{0:x}; Byte 0: 0x{1:x}'.format(int.from_bytes(self.syscon.read(2), sys.byteorder), b1))
		self.pc104 = mmap.mmap(self.fp, 4096, offset=self.Pc104Addr)
		self.pc104.seek(0)

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
		if pinNum < 64:			# EVGPIO 0-63
			self.syscon.seek(0x36) 
		else:					# EVGPIO 64-127
			self.syscon.seek(0x3a) 
		self.syscon.write_byte(0x80 | (pinNum & 63))
		self.syscon.write_byte(0)

	def clearEVGPIO(self, pinNum):
		if pinNum < 64:			# EVGPIO 0-63
			self.syscon.seek(0x36) 
		else:					# EVGPIO 64-127
			self.syscon.seek(0x3a) 
		self.syscon.write_byte(pinNum & 63)
		self.syscon.write_byte(0)

	def enPc104(self):
		self.setEVGPIO(0)
		self.setEVGPIO(1)
		self.setEVGPIO(2)
		self.setEVGPIO(3)
		self.clearEVGPIO(7)

	def DIO_Read(self, address):
		self.pc104.seek(address)
		return self.pc104.read(4)

	def DIO_Read_byte(self, address):
		self.pc104.seek(address)
		return self.pc104.read_byte()

	def DIO_Write_byte(self, address, b):
		self.pc104.seek(address)
		self.pc104.write_byte(b)
