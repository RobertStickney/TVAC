#!/usr/bin/env python3.5
import cgi
import http.server
import socketserver
import io
import time
import json
import subprocess

import SHI_MCC_Interface
from Pfeiffer_guage_Interface import *

#server_Address = ""
#server_Address = "10.0.1.201"
server_Address = "192.168.99.201"
server_Port = 8080

class MyHandler(http.server.CGIHTTPRequestHandler):

    allow_reuse_address = True
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
        print("Buffer: '" + self.cmd_buff.replace('\r', r'\r') + "'")

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
        elif self.path.startswith("/MCC_cmd/"):
            if '/get/' in self.path:
                if 'MCC_ver' in self.path:
                    buff = json.dumps(SHI_MCC_Interface.Get_ModuleVersion())
                if 'Status' in self.path:
                    buff = json.dumps(SHI_MCC_Interface.get_Status())
                elif 'ParamValues' in self.path:
                    buff = json.dumps(SHI_MCC_Interface.get_ParamValues())
                else:
                    buff = "Unkown MCC get command!"
            elif '/cmd/' in self.path:
                if '1stStageTempCTL' in self.path:  # (int(temp:0-320), int(method:0-3))
                    if self.cmd_buff_len > 0:
                        args = json.loads(self.cmd_buff)
                        if (type(args) is list) and (len(args) >= 2): 
                            buff = json.dumps(SHI_MCC_Interface.Set_FirstStageTempCTL(int(args[0]),int(args[1])))
                        else:
                            buff = "Buffer needs to be an array of two numbers."
                    else:
                        buff = "Buffer needs to be list."
                elif 'CryoPumpOn' in self.path:
                    buff = json.dumps(SHI_MCC_Interface.Turn_CryoPumpOn())
                elif 'CryoPumpOff' in self.path:
                    buff = json.dumps(SHI_MCC_Interface.Turn_CryoPumpOff())
                elif 'OpenPurgeValve' in self.path:
                    buff = json.dumps(SHI_MCC_Interface.Open_PurgeValve())
                elif 'ClosePurgeValve' in self.path:
                    buff = json.dumps(SHI_MCC_Interface.Close_PurgeValve())
                elif 'StartRegen' in self.path:       # int(num:0-4)
                    if self.cmd_buff_len > 0:
                        args = json.loads(self.cmd_buff)
                        if ((type(args) is list) and (type(args[0]) is int)): 
                            buff = json.dumps(SHI_MCC_Interface.Start_Regen(int(args[0])))
                        else:
                            buff = "Buffer needs to be an int."
                    else:
                        buff = "Buffer needs to be list."
                elif 'SetRegenParam' in self.path:    # (char(temp), int(value))
                    if self.cmd_buff_len > 0:
                        args = json.loads(self.cmd_buff)
                        if (type(args) is list) and (len(args) >= 2): 
                            buff = json.dumps(SHI_MCC_Interface.Set_RegenParam(chr(args[0]),int(args[1])))
                        else:
                            buff = "Buffer needs to be an array. 1st is a int of a char(). 2nd is a int."
                    else:
                        buff = "Buffer needs to be list."
                elif 'OpenRoughValve' in self.path:
                    buff = json.dumps(SHI_MCC_Interface.Open_RoughingValve())
                elif 'CloseRoughValve' in self.path:
                    buff = json.dumps(SHI_MCC_Interface.Close_RoughingValve())
                elif 'ClearInterlock' in self.path:
                    buff = json.dumps(SHI_MCC_Interface.Clear_RoughingInterlock())
                elif '2ndStageTempCTL' in self.path:  # int(temp:0-320)
                    if self.cmd_buff_len > 0:
                        args = json.loads(self.cmd_buff)
                        if ((type(args) is list) and (type(args[0]) is int)): 
                            buff = json.dumps(SHI_MCC_Interface.Set_SecondStageTempCTL(int(args[0])))
                        else:
                            buff = "Buffer needs to be an int."
                    else:
                        buff = "Buffer needs to be list."
                elif 'TurnTcPresOn' in self.path:
                    buff = json.dumps(SHI_MCC_Interface.Turn_TcPressureOn())
                elif 'TurnTcPresOff' in self.path:
                    buff = json.dumps(SHI_MCC_Interface.Turn_TcPressureOff())
                else:
                    buff = "Unkown MCC Command!"
            else:
                buff = "Not '/get/'' '/cmd/'"
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


print('\n'*4)
httpd = socketserver.TCPServer(( server_Address, server_Port), MyHandler )
print("Serving HTTP requests at: ", server_Address, ":", server_Port)
httpd.serve_forever()



 

