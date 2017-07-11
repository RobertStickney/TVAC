#!/usr/bin/env python3
from datetime import datetime
import time
import sys
from telnetlib import Telnet
from datetime import datetime

loopDelay = 2 # sec
ipAddr_34980A = '192.168.99.3'

#Ex: (@1002:1030,4010) Slot_1-Ch_2-30, & Slot_4-Ch_10
Channel_List = "(@2036:2040,3001:3040)"

class Keysight34980A_TC(Telnet):

    def __init__(self, host=None, port=5024, timeout=10, 
                ChannelList = "(@1001:1040,2001:2040,3001:3040)"):
        Telnet.__init__(self)
        self.Ch_List = ChannelList
        self.telnet_prompt = "Tharsis> "
        if host is not None:
            print('Connecting')
            self.open(host, port, timeout)
        
    def open(self, host, port=5024, timeout=10):
        Telnet.open(self, host, port, timeout)
        print(self.read(timeout,True))
    
    def read(self, timeout=1, try_fix_prompt=False):
        responce = self.read_until(self.telnet_prompt.encode(), timeout).decode()
        if responce.endswith(self.telnet_prompt):
            responce = responce[:-len(self.telnet_prompt)]
        else:
            raise RuntimeError("Prompt Missing or not: '{0}', Try to fix? {2}.".format(self.telnet_prompt, try_fix_prompt))
            if try_fix_prompt:
                self.write('SYST:COMM:LAN:TELN:PROM "{}"'.format(self.telnet_prompt).encode())
                self.read(1,False)
        return responce.strip()
    
    def send(self, cmd: str, timeout=1, appendLF=True, printR=False):
        if appendLF:
            cmd = cmd + '\n'
        self.write(cmd.encode())
        responce = self.read(timeout,False)
        if printR:
            print(cmd + responce)
        return responce

    def init_sys(self):
#        print(Tharsis.read_until(b"Tharsis> ",1).decode())
        dt_now = datetime.now()
        self.send("SYST:TIME {0:02d},{1:02d},{2:02d}.{3:03d}".format(dt_now.hour, dt_now.minute, dt_now.second, int(dt_now.microsecond/1000)))
        self.send("SYST:DATE {0:04d},{1:02d},{2:02d}".format(dt_now.year, dt_now.month, dt_now.day))
        self.send("SYST:DATE?")
        self.send("SYST:TIME?")
        self.send("*IDN?")
        self.send("SYST:CTYP? 1")
        self.send("SYST:CTYP? 2")
        self.send("SYST:CTYP? 3")
        self.send("DISP ON")
#        self.send("DISP OFF")
        self.send("SYST:BEEP:STAT OFF")
        self.send("CONF:TEMP TC,T")
        self.send("CONF:TEMP TC,T," + self.Ch_List)
        self.send("SENS:TEMP:ZERO:AUTO ON," + self.Ch_List)
        self.send("SENS:TEMP:TRAN:TYPE TC," + self.Ch_List)
        self.send("SENS:TEMP:TRAN:TC:TYPE T," + self.Ch_List)
        self.send("SENS:TEMP:TRAN:TC:RJUN:TYPE INT," + self.Ch_List)
        self.send("SENS:TEMP:TRAN:TC:IMP:AUTO OFF," + self.Ch_List)
        self.send("SENS:TEMP:TRAN:TC:CHECk ON," + self.Ch_List)
        self.send("UNIT:TEMP K")                                    #K=Kelven; C=°Celsius
        self.send("UNIT:TEMP K," + self.Ch_List)                    #K=Kelven; C=°Celsius
        self.send("ROUT:SCAN " + self.Ch_List)
        self.send("FORM:READ:CHAN ON")
        self.send("FORM:READ:ALAR ON")
        self.send("FORM:READ:TIME ON")
        self.send("FORM:READ:TIME:TYPE REL")
        self.send("FORM:READ:UNIT ON")
        self.send("SYST:BEEP")

    def getTC_Values(self):
        values = self.send("READ?",6).split(',')
        v1 = values[0:len(values):4]
        v2 = values[1:len(values):4]
        v3 = values[2:len(values):4]
        v4 = values[3:len(values):4]
        tc = {'num':len(v1), 'channel':[], 'unit':[], 'temp':[], 'tempC':[], 'tempF':[], 'time':[], 'alarm':[], 'valid':[], 'Working':[], 'nWorking':[], 'raw':[]}
        for i in range(tc['num']):
            tc['unit'].append(v1[i][-1])
            if tc['unit'][i] == 'K':
                tc['temp'].append(float(v1[i][:-1]))
                tc['tempC'].append(tc['temp'][i] - 273.15)
                tc['tempF'].append(tc['tempC'][i]*9/5 + 32)
            elif tc['unit'][i] == 'C':
                tc['tempC'].append(float(v1[i][:-1]))
                tc['temp'].append(tc['tempC'][i] + 273.15)
                tc['tempF'].append(tc['tempC'][i]*9/5 + 32)
            elif tc['unit'][i] == 'F':
                tc['tempF'].append(float(v1[i][:-1]))
                tc['tempC'].append((tc['tempF'][i] - 32) * 5/9)
                tc['temp'].append(tc['tempC'][i] + 273.15)
            else:
                raise RuntimeError("Unknown Units '" + v1[i] + "' ch" + v3[i])
            tc['channel'].append((int(v3[i][0])-1)*40 + int(v3[i][-3:]))
            tc['time'].append(float(v2[i]))
            tc['alarm'].append(int(v4[i]))
            if (tc['temp'][i] > 2) and (tc['temp'][i] < 1000):
                tc['valid'].append(True)
                tc['Working'].append(i)
            else:
                tc['valid'].append(False)
                tc['nWorking'].append(i)
                tc['temp'][i] = float('NaN')
                tc['tempC'][i] = float('NaN')
                tc['tempF'][i] = float('NaN')
            tc['raw'].append([v1[i], v2[i], v3[i], v4[i]])
        return tc

def printTC(TCs, num):
    try: 
        i = TCs['channel'].index(num)
    except ValueError:
        print("TC-{0:d} not in Channel List: '{1}'".format(num, Channel_List))
    else:
        if TCs['valid'][i]:
            print("TC-{0:d}: {1:.2f}K: {2:.2f}°C: {3:.2f}°F".format(num, TCs['temp'][i], TCs['tempC'][i], TCs['tempF'][i]))
        else:
            print("TC-{0:d} not working".format(num))


Tharsis = Keysight34980A_TC(ipAddr_34980A, ChannelList = Channel_List)
if (len(sys.argv)>1) and ('--init' in sys.argv):
    Tharsis.init_sys()
TCs = Tharsis.getTC_Values()

if (len(sys.argv)>1) and ('-a' in sys.argv):
    print("\nTCs not connected:")
    for i in TCs['nWorking']:
        print("TC# {0:<4d}: v1:{1}; v2:{2}; v3:{3}; v4:{4}; a={5:d}; t={6:.3f}s".format(TCs['channel'][i], TCs['raw'][i][0], TCs['raw'][i][1], TCs['raw'][i][2], TCs['raw'][i][3], TCs['alarm'][i], TCs['time'][i]))
    print("\nTCs connected:")
    for i in TCs['Working']:
        print("TC# {0:<4d}: {1:.2f}°C: {2:.2e}°F".format(TCs['channel'][i], TCs['tempC'][i], TCs['tempF'][i]))
    print('\n')

print('\n'*3)
print(datetime.today().strftime('%Y-%m-%d-%H-%M-%S'))
print("Thermocouple read time: {:.3f}s".format(TCs['time'][-1]))

# Platen 76 - 88
print("-----Platen Thermocouples (#s 76 - 80)")
for n in range(76, 80+1):
    printTC(TCs,n)
print("-----Platen Feedthough LN2 supply Thermocouple (# 85)")
printTC(TCs,85)
print("-----Platen LN2 supply Thermocouple (# 81)")
printTC(TCs,81)
print("-----Platen Vent Thermocouples (#s 82 - 84)")
for n in range(82, 84+1):
    printTC(TCs,n)
print("-----Platen Feedthrough Vent Thermocouples (#s 86 - 88)")
for n in range(86, 88+1):
    printTC(TCs,n)

# Left Shroud 96 - 100
print("-----Left Shroud Thermocouples (#s 96 - 100)")
for n in range(96, 100+1):
    printTC(TCs,n)

# Top Shroud 101 - 105
print("-----Top Shroud Thermocouples (#s 101 - 105)")
for n in range(101, 105+1):
    printTC(TCs,n)

# Right Shroud 106 - 110
print("-----Right Shroud Thermocouples (#s 106 - 110)")
for n in range(106, 110+1):
    printTC(TCs,n)

# Front Door 111 - 115
print("-----Front Door Thermocouples (#s 111 - 115)")
for n in range(111, 115+1):
    printTC(TCs,n)

# Back Door 116 - 120
print("-----Back Door Thermocouples (#s 116 - 120)")
for n in range(116, 120+1):
    printTC(TCs,n)

print("-----Shroud Feedthough LN2 supply Thermocouple (# 91)")
printTC(TCs,91)
print("-----Shroud Vent Thermocouples (#s 94 - 95)")
printTC(TCs,94)
printTC(TCs,95)
print("-----Shroud Feedthrough Vent Thermocouples (#s 92 - 93)")
printTC(TCs,92)
printTC(TCs,93)

# Chamber Wall 89-90
print("-----Chamber wall Top Thermocouple (# 89)")
printTC(TCs,89)
print("-----Chamber wall Top Thermocouple (# 90)")
printTC(TCs,90)

Tharsis.close()


