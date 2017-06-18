#!/usr/bin/env python3
import cgi
import http.server
import socketserver
import io
import time
import json
import subprocess

import SHI_MCC_Interface
import Pfeiffer_guage_Interface

#server_Address = ""
#server_Address = "10.0.1.201"
server_Address = "192.168.99.201"
server_Port = 8080

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
        elif self.path.startswith("/MCC_cmd"):
            if self.cmd_buff_len > 0:
                buff = SHI_MCC_cmd(self.cmd_buff)
            else:
                buff = ""
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
