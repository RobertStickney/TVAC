#!/usr/bin/env python3.5
import sys
import time
from threading import Thread
from tt

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


if __name__ == '__main__':

    if len(sys.argv)>1:
        tty_name = sys.argv[1]
    else:
        tty_name = '/dev/ttyxuart1'

    xuart = open(tty_name, 'r+b', buffering=0)
    xuart_listener =
    print('"{:s}" Opened.'.format(tty_name))
    if tty_name == '/dev/ttyxuart1':
        xuart.write(b'123456789012\r')
        time.sleep(5)
        xuart.write(b'Close xuart2\r')
        xuart.write(b'Quit Reader!\r')
    else:
        l = XuartListener()
        l.daemon = True
        l.start()
        print("Listener Started")
        i = 0
        while not l.close_xuart2:
            if i == 10:
                i = 0
                print(".", end='', flush=True)
            else:
                i += 1
                time.sleep(.1)
        l.xuart2.close()
        print('\nXUART2 Closed!')
    xuart.close()
    print('"{:s}" Closed.'.format(tty_name))
