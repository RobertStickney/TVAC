import socketserver

from DataContracts.ProfileInstance import ProfileInstance
from ThreadControls.ThreadCollectionInstance import ThreadCollectionInstance
from VerbHandler import VerbHandler

PORT = 8000

profileInstance = ProfileInstance.getInstance()
threadInstance = ThreadCollectionInstance.getInstance()
httpd = socketserver.TCPServer(("", PORT), VerbHandler)

print("serving")

httpd.serve_forever()