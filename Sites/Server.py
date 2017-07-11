import socketserver

from VerbHandler import VerbHandler

PORT = 8000

Handler = VerbHandler

httpd = socketserver.TCPServer(("", PORT), Handler)

print("serving")

httpd.serve_forever()