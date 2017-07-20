import http.server
import json

from Controlers.PostControl import PostContol
from DataBaseController.FileCreation import FileCreation
from DataContracts.ProfileInstance import ProfileInstance


class VerbHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        """Respond to a GET request."""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.displayZones()

    def do_POST(self):
        """Respond to a POST request."""
        try:
            contractObj = json.loads(self.getBody())
            path = self.path
            control = PostContol()
            result = {
                '/setProfile': control.loadProfile,
                '/runProfiles': control.runProfile,
                '/runSingleProfile': control.runSingleProfile,
                '/checkZoneStatus': control.checkTreadStatus,
                '/pauseZone': control.pauseSingleThread,
                '/pauseRemoveZone': control.removePauseSingleThread,
                '/holdZone': control.holdSingleThread,
                '/releaseHoldZone': control.releaseHoldSingleThread,
                '/abortZone': control.abortSingleThread,
                '/calculateRamp': control.calculateRamp
            }[path](contractObj)

            self.setHeader()
            self.wfile.write(result.encode())
        except Exception as e:
            FileCreation.pushFile("Error","Post",'{"errorMessage":"%s"}'%(e))
            self.setHeader()
            output = '{"Error":"%s"}'%(e)
            self.wfile.write(output.encode())


    def getBody(self):
        content_len = int(self.headers['content-length'])
        return self.rfile.read(content_len)

    def setHeader(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json".encode())
        self.end_headers()

    def displayZones(self):
        profileInstance = ProfileInstance.getInstance()
        self.wfile.write(profileInstance.zoneProfiles.getJson().encode())








