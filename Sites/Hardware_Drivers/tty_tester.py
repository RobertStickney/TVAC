#!/usr/bin/env python3.5
import os
import sys
import time
from threading import Thread

if __name__ == '__main__':
    sys.path.insert(0, os.getcwd())

from Hardware_Drivers.tty_reader import TTY_Reader

class XuartListener(Thread):

    def __init__(self, parent=None, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        Thread.__init__(self, group=group, target=target, name=name)
        self.args = args
        self.kwargs = kwargs
        self.parent = parent
        self.xuart2 = None
        self.close_xuart2 = False

    def run(self):
        '''
        '''
        self.xuart2 = open('/dev/ttyxuart2', 'r+b', buffering=0)
        print('Opening Xuart2')
        end = True
        buff = ''
        while end:
            buff += self.xuart2.read(1).decode()
            print('>{:s}<'.format(buff[-1:]), end='', flush=True)
            # time.sleep(1)
            if buff[-1:] == "\r":
                print('\n---{:s}---'.format(buff).replace('\r', r'\r'))
                if buff == 'Quit Reader!\r':
                    end = False
                    self.close_xuart2 = True
                if buff == 'Close xuart2\r':
                    self.close_xuart2 = True
                buff = ''
def Read_all(line_reader):
    while True:
        start_time = time.time()
        buff = line_reader(1)
        print('Read Duration: {:.4f}; Line: "{:s}"'.format(time.time()-start_time,
                                                           buff.replace('\r', r'\r')))
        if buff == '':
            break


if __name__ == '__main__':

    if len(sys.argv)>1:
        tty_name = sys.argv[1]
    else:
        tty_name = '/dev/ttyxuart1'
        # tty_name = '/dev/ttyxuart2'

    xuart = open(tty_name, 'r+b', buffering=0)
    print('"{:s}" Opened.'.format(tty_name))
    xuart = open(tty_name, 'r+b', buffering=0)
    print('"{:s}" Opened again.'.format(tty_name))
    xuart_listener = TTY_Reader(xuart)
    xuart_listener.daemon = True
    xuart_listener.start()
    if tty_name == '/dev/ttyxuart1':
        print('Read buffer at startup:')
        Read_all(xuart_listener.read_line)
        print('Start writing to Xuart1!')
        start_time = time.time()
        for i in range(30):
            xuart.write(b'123456789012\r')
            xuart.write(b'Line with CR at end.\r')
            xuart.write(b'Line without CR at end. ')
            xuart.write('i = {:d}\r'.format(i).encode())
        time.sleep(2)
        xuart.write(b'Close xuart\r')
        xuart.write(b'0123456789\r')
        print('Done writing in {:.2f} seconds!'.format(time.time() - start_time))
        print('Read buffer before ending:')
        Read_all(xuart_listener.read_line)
    else:
        line = ''
        while line != 'Close xuart\r':
            start_time = time.time()
            line = xuart_listener.read_line(1)
            if line == '':
                print(".", end='', flush=True)
            else:
                print('\nRead Duration: {:.4f}; Line: "{:s}"'.format(time.time() - start_time,
                                                                 line.replace('\r', r'\r')))
                xuart.write(line.encode())
    xuart.close()
    print('"{:s}" Closed.'.format(tty_name))
