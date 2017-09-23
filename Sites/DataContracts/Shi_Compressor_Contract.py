import threading


class Shi_Compressor_Contract:

    __Lock = threading.RLock()

    def __init__(self):
        self.return_pressure = 0
        self.water_in_temp = 0
        self.water_out_temp = 0

    def update(self, d):
        self.__Lock.acquire()
        if 'Return Pressure' in d:
            self.return_pressure = d['Return Pressure']
        if 'Water In Temp' in d:
            self.water_in_temp = d['Water In Temp']
        if 'Water Out Temp' in d:
            self.water_out_temp = d['Water Out Temp']
        self.__Lock.release()

    def getVal(self, name):
        self.__Lock.acquire()
        if name == 'Return Pressure':
            val = self.return_pressure
        elif name == 'Water In Temp':
            val = self.water_in_temp
        elif name == 'Water Out Temp':
            val = self.water_out_temp
        else:  # Unknown Value!
            val = None
        self.__Lock.release()
        return val

    def getJson(self):
        self.__Lock.acquire()
        message = []
        message.append('{"Return Pressure":%s,' % self.return_pressure)
        message.append('"Water In Temp":%s,' % self.water_in_temp)
        message.append('"Water Out Temp":%s}' % self.water_out_temp)
        self.__Lock.release()
        return ''.join(message)
