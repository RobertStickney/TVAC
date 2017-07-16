import http.server
import json

from Controlers.PostControl import PostContol
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

        contractObj = json.loads(self.getBody())
        path = self.path
        control = PostContol()

        result = {
            '/setProfile': control.loadProfile,
            '/runProfiles': control.runProfile,
            '/runSingleProfile': control.runSingleProfile,
            '/checkThreadStatus': control.checkTreadStatus,
            '/pauseThread': control.pauseSingleThread,
            '/pauseRemoveThread': control.removePauseSingleThread
        }[path](contractObj)


        self.setHeader()
        self.displayZones()

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








