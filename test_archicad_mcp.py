"""Self-check against a fake Archicad. Run: uv run --with "mcp>=2.3,<3" python test_archicad_mcp.py"""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import archicad_mcp

FAKE_PORT = 19725  # not the first port, so port discovery is exercised


class FakeArchicad(BaseHTTPRequestHandler):
    def do_POST(self):
        request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        command = request["command"]
        if command == "API.IsAlive":
            reply = {"succeeded": True, "result": {"isAlive": True}}
        elif command == "API.GetElementsByType":
            reply = {"succeeded": True, "result": {"elements": [{"elementId": {"guid": "W1"}}]}}
        elif command == "API.ExecuteAddOnCommand":
            name = request["parameters"]["addOnCommandId"]["commandName"]
            reply = {"succeeded": True, "result": {"addOnCommandResponse": {"echo": name}}}
        else:
            reply = {"succeeded": False, "error": {"code": 4001, "message": "unknown command"}}
        payload = json.dumps(reply).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass


server = HTTPServer(("127.0.0.1", FAKE_PORT), FakeArchicad)
threading.Thread(target=server.serve_forever, daemon=True).start()

walls = archicad_mcp.archicad_command("API.GetElementsByType", {"elementType": "Wall"})
assert walls == {"elements": [{"elementId": {"guid": "W1"}}]}, walls

assert archicad_mcp.tapir_command("GetProjectInfo") == {"echo": "GetProjectInfo"}

try:
    archicad_mcp.archicad_command("API.Bogus")
    raise AssertionError("expected ArchicadError")
except archicad_mcp.ArchicadError as error:
    assert "unknown command" in str(error)

server.shutdown()
archicad_mcp.PORTS = range(19790, 19792)  # nothing listens here
try:
    archicad_mcp.archicad_command("API.GetProductInfo")
    raise AssertionError("expected ArchicadError")
except archicad_mcp.ArchicadError as error:
    assert "No running Archicad" in str(error)

print("ok")
