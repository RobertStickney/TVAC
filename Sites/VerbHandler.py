import http.server
import json
import time
from ShiMcc import ShiMcc
import _thread

from ZoneContract import ZoneContract
from ZonesInstance import ZonesInstance

class VerbHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        """Respond to a GET request."""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.displayZones()

    def do_POST(self):
        """Respond to a POST request."""
        content_len = int(self.headers['content-length'])
        post_body = self.rfile.read(content_len)
        contractObj = ZoneContract(json.loads(post_body))

        noIdea = ShiMcc()
        _thread.start_new_thread(noIdea.getChecksum, ("a",))
        #zonesInstance = ZonesInstance.getInstance()
        #zonesInstance.zones.update(contractObj)

        self.send_response(200)
        self.send_header("Content-type", "application/json".encode())
        self.end_headers()
        self.displayZones()

    def displayZones(self):
        zonesInstance = ZonesInstance.getInstance()
        message = []
        message.append("[")
        message.append(json.dumps(zonesInstance.zones.getZone("zone1").__dict__))
        message.append(",")
        message.append(json.dumps(zonesInstance.zones.getZone("zone2").__dict__))
        message.append(",")
        message.append(json.dumps(zonesInstance.zones.getZone("zone3").__dict__))
        message.append(",")
        message.append(json.dumps(zonesInstance.zones.getZone("zone4").__dict__))
        message.append(",")
        message.append(json.dumps(zonesInstance.zones.getZone("zone5").__dict__))
        message.append(",")
        message.append(json.dumps(zonesInstance.zones.getZone("zone6").__dict__))
        message.append(",")
        message.append(json.dumps(zonesInstance.zones.getZone("zone7").__dict__))
        message.append(",")
        message.append(json.dumps(zonesInstance.zones.getZone("zone8").__dict__))
        message.append(",")
        message.append(json.dumps(zonesInstance.zones.getZone("zone9").__dict__))
        message.append("]")
        self.wfile.write(''.join(message).encode())








