#!/usr/bin/env python3
import socketserver
import sys

from VerbHandler import VerbHandler
from Collections.ProfileInstance import ProfileInstance
from Collections.HardwareStatusInstance import HardwareStatusInstance
from ThreadControls.ThreadCollectionInstance import ThreadCollectionInstance


from HouseKeeping import globalVars
from HouseKeeping.globalVars import debugPrint
# Adding verbose level for debug printing
verbos = 0

class ReuseAddrTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


if __name__ == '__main__':
    # adding debug info
    globalVars.init()
    if(len(sys.argv)>1):
        for arg in sys.argv:
            if arg.startswith("-v"):
                globalVars.verbos = arg.count("v")
    debugPrint(1,"Debug on: Level " + str(globalVars.verbos))

    PORT = 8000

    debugPrint(1,"Starting initializing threads and drivers")
    
    hardwareStatusInstance = HardwareStatusInstance.getInstance()
    profileInstance = ProfileInstance.getInstance()
    threadInstance = ThreadCollectionInstance.getInstance()
    

    
    debugPrint(1,"Finished initializing threads and drivers")
    
    httpd = ReuseAddrTCPServer(("", PORT), VerbHandler)

    print("Set up is complete. Starting to server request...")

    httpd.serve_forever()