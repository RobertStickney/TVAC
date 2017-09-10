#!/usr/bin/env python3.5
import cgi
import http.server
import socketserver

class MyHandler(http.server.CGIHTTPRequestHandler):

    cgi_directories = ""

    def printCommand(self):
        print("Command:", self.command)

    def printPath(self):
        print("Path:", self.path)

    def printHeaders(self):
        headers = self.headers
        for h in headers:
            print("H -", h, ":", headers[h])

    def printBuffer(self):
        print("Buffer: '", self.rfile.read(int(self.headers['Content-Length'])))

    def printRequest(self):
        self.printCommand()
        self.printPath()
        self.printHeaders()
        self.printBuffer()

    def do_GET(self):
        self.printRequest()
        http.server.CGIHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        self.printRequest()
        buff = ""
        if self.path == "\hello":
        self.send_response(200)
            buff = "Here is: " + self.path + "- Nice address!"
        elif self.path == "\json":
            buff = "do json work here"
        self.send_header('Content-Length', len(buff))
        self.end_headers()
        self.wfile.write(buff.encode())
#       self.wfile.write(b'\n' + buff.encode)
#       self.end_headers()
#       http.server.CGIHTTPRequestHandler.do_POST(self)

    def do_PUT(self):
        self.printRequest()
        http.server.CGIHTTPRequestHandler.do_PUT(self)

    def do_HEAD(self):
        self.printRequest()
        http.server.CGIHTTPRequestHandler.do_HEAD(self)


httpd = socketserver.TCPServer(( 'whitestar', 8080 ), MyHandler )
httpd.serve_forever()
