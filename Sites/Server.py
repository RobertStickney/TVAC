#!/usr/bin/env python3
import socketserver

from DataContracts.ProfileInstance import ProfileInstance
from DataContracts.HardwareStatusInstance import HardwareStatusInstance
from ThreadControls.ThreadCollectionInstance import ThreadCollectionInstance
from VerbHandler import VerbHandler

PORT = 8000

hardwareStatusInstance = HardwareStatusInstance.getInstance()
profileInstance = ProfileInstance.getInstance()
threadInstance = ThreadCollectionInstance.getInstance()

httpd = socketserver.TCPServer(("", PORT), VerbHandler)

print("serving")

httpd.serve_forever()