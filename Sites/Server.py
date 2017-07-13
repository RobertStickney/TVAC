import socketserver

from DataContracts.ProfileInstance import ProfileInstance
from VerbHandler import VerbHandler

PORT = 8000

Handler = VerbHandler
profileInstance = ProfileInstance.getInstance()

httpd = socketserver.TCPServer(("", PORT), Handler)

print("serving")

httpd.serve_forever()