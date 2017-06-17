#!/usr/bin/env python3
import cgi
import http.server
import socketserver
import io
import time
import json
import subprocess


#server_Address = ""
server_Address = "10.0.1.201"
#server_Address = "192.168.99.201"
server_Port = 8080

def SHI_MCC_cmd(Command):
    p_gauge = open('/dev/ttyxuart2', 'r+b', buffering=0)
    p_gauge.write(Command.encode())
    time.sleep(0.060)
    temp = p_gauge.read(113)
    print("R:--" + temp.decode().replace('\r', r'\r') + "---")
    return temp.decode()

def SHI_MCC_GetChecksum(cmd):    #append the sum of the string's bytes mod 256 + '\r'
    d = sum(cmd.encode())
    #       0x30 + ( (d2 to d6) or (d0 xor d6) or ((d1 xor d7) shift to d2)                            
    return  0x30 + ( (d & 0x3c) | 
                    ((d & 0x01) ^ ((d & 0x40) >> 6)) | # (d0 xor d6)
                    ((d & 0x02) ^ ((d & 0x80) >> 6)) ) # (d1 xor d7)

def SHI_MCC_GenCmd(cmd): #Cmd syntax see page MCC Programing Guide
    return "${0}{1:c}\r".format(cmd, SHI_MCC_GetChecksum(cmd))


def SHI_MCC_ResponceGood(Address, Responce, Parm=349):
    print("R:--" + Responce.replace('\r', r'\r') + "---")
    if Responce[-1] != '\r':
        print("R:--" + Responce.replace('\r', r'\r') + "--- Missing Carriage Return at the end")
        return False
    if int(Responce[-4:-1]) != Pfeiffer_GetChecksum(Responce[:-4]):
        print("R:--" + Responce.replace('\r', r'\r') + "---","Checksum:" + str(Pfeiffer_GetChecksum(Responce[:-4])) + "Failure")
        return False
    if int(Responce[:3]) != Address:
        print("R:--" + Responce.replace('\r', r'\r') + "---","Address:",str(Address),"Failure")
        return False
    if int(Responce[5:8]) != Parm:
        print("R:--" + Responce.replace('\r', r'\r') + "---","Param:",str(Parm),"Failure")
        return False
    if int(Responce[8:10]) != (len(Responce) - 14):
        print("R:--" + Responce.replace('\r', r'\r') + "---","Payload size:",str(len(Responce) - 14),"Failure"+Responce[8:10])
        return False
    return True # Yea!! respomnce seems ok

def SHI_MCC_DataRequest(Address, Parm=349):
    p_gauge = open('/dev/ttyxuart2', 'r+b', buffering=0)
    for tries in range(5):
        p_gauge.write(Pfeiffer_GenCmdRead(Address,Parm).encode())
        time.sleep(0.060*(tries+1))
        Resp = p_gauge.read(113*(tries+1)).decode()
        if Pfeiffer_ResponceGood(Address, Resp, Parm):
            break
        print("Try number:" + str(tries))
    else:
        print("No more tries! Something is wrong!")
        Resp = "{:*^32}".format('Timeout!')
    p_gauge.close
    return Resp[10:-4]



def Pfeiffer_Vac(Command):
    p_gauge = open('/dev/ttyxuart0', 'r+b', buffering=0)
    p_gauge.write(Command.encode())
    time.sleep(0.060)
    temp = p_gauge.read(113)
    print("R:--" + temp.decode().replace('\r', r'\r') + "---")
    return temp.decode()

def Pfeiffer_GetChecksum(cmd):  #append the sum of the string's bytes mod 256 + '\r'
    return sum(cmd.encode())%256

def Pfeiffer_applyChecksum(cmd):  #append the sum of the string's bytes mod 256 + '\r'
    return "{0}{1:03d}\r".format(cmd, Pfeiffer_GetChecksum(cmd))

def Pfeiffer_GenCmdRead(Address, Parm=349): #Cmd syntax see page #16 of MPT200 Operating instructions
    return Pfeiffer_applyChecksum("{:03d}00{:03d}02=?".format(Address, Parm))

def Pfeiffer_GenCmdWrite(Address,Parm,dataStr): #Cmd syntax on page #16 of MPT200 Operating instructions
    return Pfeiffer_applyChecksum("{0:03d}10{1:03d}{2:02d}{3}".format(Address, Parm, len(dataStr), dataStr))

def Pfeiffer_ResponceGood(Address, Responce, Parm=349):
    print("R:--" + Responce.replace('\r', r'\r') + "---")
    if Responce[-1] != '\r':
        print("R:--" + Responce.replace('\r', r'\r') + "--- Missing Carriage Return at the end")
        return False
    if int(Responce[-4:-1]) != Pfeiffer_GetChecksum(Responce[:-4]):
        print("R:--" + Responce.replace('\r', r'\r') + "---","Checksum:" + str(Pfeiffer_GetChecksum(Responce[:-4])) + "Failure")
        return False
    if int(Responce[:3]) != Address:
        print("R:--" + Responce.replace('\r', r'\r') + "---","Address:",str(Address),"Failure")
        return False
    if int(Responce[5:8]) != Parm:
        print("R:--" + Responce.replace('\r', r'\r') + "---","Param:",str(Parm),"Failure")
        return False
    if int(Responce[8:10]) != (len(Responce) - 14):
        print("R:--" + Responce.replace('\r', r'\r') + "---","Payload size:",str(len(Responce) - 14),"Failure"+Responce[8:10])
        return False
    return True # Yea!! respomnce seems ok

def Pfeiffer_DataRequest(Address, Parm=349):
    p_gauge = open('/dev/ttyxuart0', 'r+b', buffering=0)
    for tries in range(5):
        p_gauge.write(Pfeiffer_GenCmdRead(Address,Parm).encode())
        time.sleep(0.060*(tries+1))
        Resp = p_gauge.read(113*(tries+1)).decode()
        if Pfeiffer_ResponceGood(Address, Resp, Parm):
            break
        print("Try number:" + str(tries))
    else:
        print("No more tries! Something is wrong!")
        Resp = "{:*^32}".format('Timeout!')
    p_gauge.close
    return Resp[10:-4]

def Pfeiffer_GetPressure(Address): # Pfeifer returns pressure in hPa
    buff = Pfeiffer_DataRequest(Address, 740)
    if (len(buff)==6 and buff.isdigit):
        return float((int(buff[:4])/1000)*10**(int(buff[-2:])-20))
    print('Data:' + buff + '')

class MyHandler(http.server.CGIHTTPRequestHandler):

    cgi_directories = ""
    cmd_buff_len = 0
    cmd_buff = ""

    def printCommand(self):
        print("Command:", self.command)

    def printPath(self):
        print("Path:", self.path)

    def printHeaders(self):
        headers = self.headers
        for h in headers:
            print("H -", h, ":", headers[h])

    def getBuff(self):
        self.cmd_buff_len = int(self.headers['Content-Length'])
        if self.cmd_buff_len > 0:
            self.cmd_buff = self.rfile.read(self.cmd_buff_len).decode()
        else:
            self.cmd_buff = ""

    def printBuffer(self):
        print("Buffer: '", self.cmd_buff.replace('\r', r'\r'), "'")

    def printRequest(self):
        self.printCommand()
        self.printPath()
        self.printHeaders()
        self.printBuffer()

    def do_GET(self):
        self.printRequest()
        http.server.CGIHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        self.getBuff()
        self.printRequest()
        if self.path == "/hello":
            buff = "Here is: " + self.path + "- Nice address!"
        elif self.path == "/json":
            print("JSON recieved: '" + self.cmd_buff + "'\n")
            t1 = json.loads(self.cmd_buff)
            t1['d1'] = t1['d1'] + 40.1
            buff = json.dumps(t1)
        elif self.path == "/xuart0":
            buff = Pfeiffer_DataRequest(1)
        elif self.path == "/Pgauge":
            if self.cmd_buff_len > 0:
                gauges = json.loads(self.cmd_buff)
            else:
                gauges = [1]
            if type(gauges) is not list:
                gauges = [1]
            resp = dict(Pressure = [], Kind = [], Addr = [])
            for gauge in gauges:
                resp['Addr'].append(gauge) 
                resp['Kind'].append(Pfeiffer_DataRequest(gauge))
                resp['Pressure'].append(Pfeiffer_GetPressure(gauge))
            buff = json.dumps(resp)
        elif self.path.startswith("/setPin"):
            setPin = json.loads(self.cmd_buff)
            setPin.insert(0, 'tsctl-noncavium')
            setPin.insert(1, 'DIO')
            setPin.insert(2, 'SetAsync')
            print(setPin)
            buff = json.dumps(subprocess.check_call(setPin))
        elif self.path.startswith("/getPins"):
            resp = dict(PinsOut = [], PinsIn = [])
            for i in range(1, 6+1):
                resp['PinsOut'].append(subprocess.check_output([
                    "tsctl-noncavium", 
                    "DIO", 
                    "GetAsync", 
                    "8820_out{:d}".format(i)], universal_newlines=True))
            for i in range(1, 14+1):
                resp['PinsIn'].append(subprocess.check_output([
                    "tsctl-noncavium", 
                    "DIO", 
                    "GetAsync", 
                    "8820_in{:d}".format(i)], universal_newlines=True))
            buff = json.dumps(resp)
        else:
            buff = "Unkown Command!"
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-Length', len(buff))
        self.end_headers()
        self.wfile.write(buff.encode())
        print("Responce Buffer: '", buff.replace('\r', r'\r'), "'\n--------\n")

    def do_PUT(self):
        self.printRequest()
        http.server.CGIHTTPRequestHandler.do_PUT(self)

    def do_HEAD(self):
        self.printRequest()
        http.server.CGIHTTPRequestHandler.do_HEAD(self)


httpd = socketserver.TCPServer(( server_Address, server_Port), MyHandler )
print("Serving HTTP requests at: ", server_Address, ":", server_Port)
httpd.serve_forever()
