import time
import sys
from Testing_mmap import TS_Registers

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
