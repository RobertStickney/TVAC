import threading

class ThermocoupleContract:

    __lock = threading.RLock()

    def __init__(self, d):
        self.Thermocouple = d
        self.temp = 0
        self.working = False
        self.userDefined = False


        self.time = 0
        self.alarm = 0

    def update(self, d):
        self.__lock.acquire()
        if 'time' in d:  # time offset from start of scan
            self.time = d['time']
        if 'temp' in d:  # all temperatures are in Kelven
            self.temp = d['temp']
        if 'working' in d:
            self.working = d['working']
        if 'userDefined' in d:
            self.userDefined = d['userDefined']
        if 'alarm' in d:
            self.alarm = d['alarm']
        self.__lock.release()

    def getNum(self):
        return self.Thermocouple

    def getTemp(self, temp_units = 'K'):
        self.__lock.acquire()
        # temp_units values: ['K', 'C', 'F']
        if temp_units == 'C':
            temp = self.temp - 273.15
        elif temp_units == 'F':
            temp = (self.temp - 273.15)*9/5 + 32
        else:
            temp = self.temp
        self.__lock.release()
        return temp

    def getWorking():
        self.__lock.acquire()
        tmp = self.working 
        self.__lock.release()
        return tmp

    def getTime():
        self.__lock.acquire()
        tmp = self. time
        self.__lock.release()
        return tmp

    def getAlarm():
        self.__lock.acquire()
        tmp = self. alarm
        self.__lock.release()
        return tmp


    def getJson(self, temp_units = 'K'):
        self.__lock.acquire()
        # temp_units values: ['K', 'C', 'F']
        message = []
        message.append('{"thermocouple":%s,' % self.Thermocouple)
        message.append('"time":%s,' % self.time)
        message.append('"temp":%s,' % self.getTemp(temp_units))
        message.append('"working":%s,' % self.working)
        message.append('"alarm":%s}' % self.alarm)
        self.__lock.release()
        return ''.join(message)
