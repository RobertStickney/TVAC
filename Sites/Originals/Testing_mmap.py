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

def test_mmap():
	ts = TS_Registers()
	ts.open_Registers()

	sleeptime = 0.1
	ts.LED_Red_off()
	ts.LED_Green_off()

	for i in range(10):
		ts.LED_Red_on()
		time.sleep(sleeptime)
		ts.LED_Green_on()
		time.sleep(sleeptime)
		ts.LED_Red_off()
		time.sleep(sleeptime)
		ts.LED_Green_off()
		time.sleep(sleeptime)

	ts.close()

def setup_pc104():
	regs = TS_Registers()
	regs.open_Registers()
	regs.enPc104()
	regs.pc104.seek(regs.Dio1_Addr(0))
	print("1st DIO64 Board ID: 0x{:02x} 0x{:02x}".format(regs.pc104.read_byte(), regs.pc104.read_byte()))
	regs.pc104.seek(regs.Dio2_Addr(0))
	print("2nd DIO64 Board ID: 0x{:02x} 0x{:02x}".format(regs.pc104.read_byte(), regs.pc104.read_byte()))
	regs.pc104.seek(regs.Adc16Addr(0))
	print("ADC-16 Board ID: 0x{:02x} 0x{:02x} \n".format(regs.pc104.read_byte(), regs.pc104.read_byte()))
	return regs


if __name__ == '__main__':
	#test_mmap()
	ts = setup_pc104()

	if (len(sys.argv)>2):
		if sys.argv[1] == 'di':
			if sys.argv[2] == '2':
				addr = ts.Dio2_Addr(ts.DioInBaseAddr)
			else:
				addr = ts.Dio1_Addr(ts.DioInBaseAddr)
			b = ts.DIO_Read(addr)
			print(type(b))
			print("DIO address: {:x} bytes: 0x{:02x} {:02x} {:02x} {:02x}".format(addr, 
											ts.DIO_Read_byte(addr+3), 
											ts.DIO_Read_byte(addr+2), 
											ts.DIO_Read_byte(addr+1), 
											ts.DIO_Read_byte(addr+0)))
		elif sys.argv[1] == 'do':
			if (len(sys.argv)>4):
				pinN = 31 & int(sys.argv[4])
				addr = (pinN >> 3) + ts.DioOutBaseAddr
				if sys.argv[2] == '2':
					addr = ts.Dio2_Addr(addr)
				else:
					addr = ts.Dio1_Addr(addr)
				b = ts.DIO_Read_byte(addr)
				print("DIO address: {:x} byte: {:02x}".format(addr, b))
				if sys.argv[3] == 'set':
					b |= 0x01 << (7 & pinN)
				elif sys.argv[3] == 'clear':
					b &= 0xfe << (7 & pinN)
				ts.DIO_Write_byte(addr, b)
				print("Write byte: 0x{:x}".format(b))





	ts.close()
