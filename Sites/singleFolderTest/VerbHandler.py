import http.server
import json

# from Controllers.PostControl import PostContol
# from Controllers.GetControl import GetControl
# from DataBaseController.FileCreation import FileCreation
# from Collections.ProfileInstance import ProfileInstance
#
# from HouseKeeping.globalVars import debugPrint
from PostControl import PostContol
from GetControl import GetControl
from FileCreation import FileCreation
from ProfileInstance import ProfileInstance

from globalVars import debugPrint

class VerbHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        """Respond to a GET request."""
        debugPrint(1,"Received GET Request")
        try:
            body = self.getBody()
            if type(body) == type(b'a'):
                debugPrint(3,"Changing body from bytes to String")
                body = body.decode("utf-8")
            contractObj = json.loads(body)
            path = self.path
            debugPrint(3,"On path: '{}'".format(path))
            control = GetControl()

            result = {
                '/checkZoneStatus': control.checkTreadStatus,
                '/getAllThermoCoupleData': control.getAllThermoCoupleData,
                '/getAllZoneData': control.getAllZoneData,
                '/getPC104_Digital': control.getPC104_Digital,
                '/getPC104_Analog': control.getPC104_Analog,
                '/getLastError' : control.getLastError
            }[path](contractObj)

            debugPrint(1,"Sending results")
            self.setHeader()
            self.wfile.write(result.encode())
        except Exception as e:
            print("There has been an error")
            FileCreation.pushFile("Error","Post",'{"errorMessage":"%s"}\n'%(e))
            self.setHeader()
            output = '{"Error":"%s"}\n'%(e)
            self.wfile.write(output.encode())

        # self.send_response(200)
        # self.send_header("Content-type", "application/json")
        # self.end_headers()
        # self.displayZones()

        # self.wfile.write("Hello \n".encode())
        # Basic status update...
        # UUID
        # Current pressure
        # Which Thermalcouple are running, and current status

        # get Thermalcouple

    def do_POST(self):
        """Respond to a POST request."""
        debugPrint(1,"Received Post Request")
        # try:
        body = self.getBody()
        if type(body) == type(b'a'):
            debugPrint(3,"Changing body from bytes to String")
            body = body.decode("utf-8")
        contractObj = json.loads(body)
        path = self.path
        debugPrint(3,"on path: '{}'".format(path))
        control = PostContol()
        result = {
            '/setProfile': control.loadProfile,
            '/runProfiles': control.runProfile,
            '/runSingleProfile': control.runSingleProfile,
            # '/checkZoneStatus': control.checkTreadStatus,
            '/pauseZone': control.pauseSingleThread,
            '/pauseRemoveZone': control.removePauseSingleThread,
            '/holdZone': control.holdSingleThread,
            '/releaseHoldZone': control.releaseHoldSingleThread,
            '/abortZone': control.abortSingleThread,
            '/calculateRamp': control.calculateRamp,
            '/setDigital': control.setPC104_Digital,  #TODO: Remove this Engeering function!
            '/setAnalog': control.setPC104_Analog  #TODO: Remove this Engeering function!
        }[path](contractObj)

        self.setHeader()
        self.wfile.write(result.encode())
        # except Exception as e:
        #     print("There has been an error")
        #     FileCreation.pushFile("Error","Post",'{"errorMessage":"%s"}\n'%(e))
        #     self.setHeader()
        #     output = '{"Error":"%s"}\n'%(e)
        #     self.wfile.write(output.encode())


    def getBody(self):
        content_len = int(self.headers['content-length'])
        tempStr = self.rfile.read(content_len)
        return tempStr

    def setHeader(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json".encode())
        self.end_headers()

    def displayZones(self):
        profileInstance = ProfileInstance.getInstance()
        self.wfile.write(profileInstance.zoneProfiles.getJson().encode())








