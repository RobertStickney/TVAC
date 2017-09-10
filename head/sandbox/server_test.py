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
server_Address = "127.0.0.1"
#server_Address = "10.0.1.201"
#server_Address = "192.168.99.201"
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
            buff = json.dumps(subprocess.check_call(setPin))
        elif self.path.startswith("/getPins"):
            buff = json.dumps(resp)
        elif self.path.startswith("/MCC_cmd/"):
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

if __name__ == '__main__':
	print('\n'*4)
	httpd = socketserver.TCPServer(( server_Address, server_Port), MyHandler )
	print("Serving HTTP requests at: ", server_Address, ":", server_Port)
	httpd.serve_forever()



 

