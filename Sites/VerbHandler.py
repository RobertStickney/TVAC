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
            '/checkThreadStatus': control.checkTreadStatus
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
        zonesInstance = ProfileInstance.getInstance()
        message = []
        # message.append("[")
        # message.append(json.dumps(zonesInstance.zoneProfiles.getZone("zone1").__dict__))
        # message.append(",")
        # message.append(json.dumps(zonesInstance.zoneProfiles.getZone("zone2").__dict__))
        # message.append(",")
        # message.append(json.dumps(zonesInstance.zoneProfiles.getZone("zone3").__dict__))
        # message.append(",")
        # message.append(json.dumps(zonesInstance.zoneProfiles.getZone("zone4").__dict__))
        # message.append(",")
        # message.append(json.dumps(zonesInstance.zoneProfiles.getZone("zone5").__dict__))
        # message.append(",")
        # message.append(json.dumps(zonesInstance.zoneProfiles.getZone("zone6").__dict__))
        # message.append(",")
        # message.append(json.dumps(zonesInstance.zoneProfiles.getZone("zone7").__dict__))
        # message.append(",")
        # message.append(json.dumps(zonesInstance.zoneProfiles.getZone("zone8").__dict__))
        # message.append(",")
        # message.append(json.dumps(zonesInstance.zoneProfiles.getZone("zone9").__dict__))
        # message.append("]")
        self.wfile.write(''.join(message).encode())








