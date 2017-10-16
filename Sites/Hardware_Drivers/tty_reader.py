#!/usr/bin/env python3.5
from threading import Thread
# from threading import RLock
# from threading import Event
from threading import Condition


class TTY_Reader(Thread):

    __lock = Condition()
    # __newline = Event()

    def __init__(self, fd, group=None, target=None, name=None, args=(), kwargs=None):
        Thread.__init__(self, group=group, target=target, name=name)
        self.args = args
        self.kwargs = kwargs
        self.tty_fd = fd
        self.buffer = ['']
        # self.lines

    def run(self):
        '''
        '''
        while not self.tty_fd.closed:
            buff = self.tty_fd.read(1).decode()
            # print('>{:s}<'.format(buff).replace('\r', r'\r'), end='', flush=True)
            with self.__lock:
                # self.__newline.clear()
                self.buffer[0] += buff
                if buff == "\r" or len(self.buffer[0]) >= 128:
                    # print('\n---{:s}---'.format(buff[0]).replace('\r', r'\r'))
                    self.buffer.insert(0, "")
                    self.__lock.notify()
                    # self.__newline.set()

    def flush_buffer(self):
        with self.__lock:
            self.buffer = ['']

    def read_line(self, time_out):
        with self.__lock:
            if len(self.buffer) > 1:
                line = self.buffer.pop()
            else:
                self.__lock.wait(time_out)  # wait for a new line to put onto the buffer
                if len(self.buffer) > 1:
                    line = self.buffer.pop()
                elif len(self.buffer) == 1:
                    line = self.buffer[0]
                    self.buffer[0] = ''
                else:
                    line = ''
                    self.buffer = ['']
        return line


if __name__ == '__main__':
    pass
