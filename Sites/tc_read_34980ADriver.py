#!/usr/bin/env python3
from datetime import datetime
import sys
from datetime import datetime
from tc_read_34980A import Keysight34980A_TC

loopDelay = 2 # sec
ipAddr_34980A = '192.168.99.3'

#Ex: (@1002:1030,4010) Slot_1-Ch_2-30, & Slot_4-Ch_10
Channel_List = "(@2036:2040,3001:3040)"

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


