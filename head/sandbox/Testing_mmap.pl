#!/usr/bin/env python3
import os
import sys
import mmap

def bits_clear(mm, pos, byte)
    mm.seek()

fp = os.open('/dev/mem', os.O_RDWR|os.O_NONBLOCK|os.O_SYNC)
mm = mmap.mmap(fp, 4096, offset=0x80004000)

t1 = mm.read_byte()
print(type(t1))
mm.seek(0)
print('Board Model #: 0x{0:x}; Byte 0: 0x{1:x}'.format(int.from_bytes(mm.read(2), sys.byteorder), t1))

mm.seek(0x12)
t1 = int.from_bytes(mm.read(2), sys.byteorder)
#t2 = (t1 | 0x1800).to_bytes(2, sys.byteorder)
print(type(t2))
mm.seek(0x12)
mm.write((t1 | 0x1800).to_bytes(2, sys.byteorder))

mm.seek(0x13)
t1 = mm.read_byte()
#t2 = (t1 | 0x1800).to_bytes(2, sys.byteorder)
mm.seek(0x13)
mm.write((t1 | 0x1).to_bytes(2, sys.byteorder))



mm.close()
os.close(fp)
