# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=2.3,<3"]
# ///
"""MCP server that lets Claude drive a running Archicad (25+) through its local JSON API."""

import json
import urllib.request

from mcp.server.mcpserver import MCPServer

HOST = "http://127.0.0.1"
# Archicad picks the first free port in this range; several open instances get consecutive ports.
PORTS = range(19723, 19745)
TIMEOUT_SECONDS = 60

mcp = MCPServer("archicad")


class ArchicadError(Exception):
    """Archicad is unreachable or rejected a command."""


@mcp.tool()
def archicad_command(command: str, parameters: dict | None = None) -> dict:
    """Run a built-in Archicad JSON API command and return its result.

    Common commands:
    - API.GetProductInfo
    - API.GetElementsByType  {"elementType": "Wall" | "Slab" | "Zone" | "Door" | "Window" | ...}
    - API.GetAllElements
    - API.GetSelectedElements
    - API.GetAllPropertyIds  {"propertyType": "UserDefined" | "BuiltIn"}
    - API.GetPropertyIds     {"properties": [{"type": "BuiltIn", "nonLocalizedName": "General_ElementID"}]}
    - API.GetDetailsOfProperties  {"properties": [{"propertyId": {...}}]}
    - API.GetPropertyValuesOfElements  {"elements": [{"elementId": {...}}], "properties": [{"propertyId": {...}}]}
    - API.SetPropertyValuesOfElements  {"elementPropertyValues": [...]}
    - API.GetClassificationSystems, API.GetClassificationsOfElements, API.SetClassificationsOfElements
    - API.GetNavigatorItemTree, API.GetLayoutSettings
    Full reference: https://archicadapi.graphisoft.com/JSONInterfaceDocumentation/
    """
    return _post(command, parameters or {})


@mcp.tool()
def tapir_command(command: str, parameters: dict | None = None) -> dict:
    """Run a Tapir add-on command (needs the Tapir add-on installed in Archicad).

    Tapir adds what the built-in API lacks, e.g. CreateColumns, CreateSlabs, CreatePolylines,
    GetDetailsOfElements, SetDetailsOfElements, MoveElements, DeleteElements, GetSelectedElements,
    ChangeSelectionOfElements, GetProjectInfo, GetStoryInfo, PublishPublisherSet, ExecuteHotlinks,
    GetAttributesByType, CreateLayers, ReloadLibraries, GenerateDocumentation.
    Command list and schemas: https://enzyme-apd.github.io/tapir-archicad-automation/
    """
    response = _post(
        "API.ExecuteAddOnCommand",
        {
            "addOnCommandId": {"commandNamespace": "TapirCommand", "commandName": command},
            "addOnCommandParameters": parameters or {},
        },
    )
    return response.get("addOnCommandResponse", response)


def _post(command: str, parameters: dict) -> dict:
    body = json.dumps({"command": command, "parameters": parameters}).encode()
    reply = _send(_find_port(), body)
    if not reply.get("succeeded"):
        raise ArchicadError(f"{command} failed: {json.dumps(reply.get('error', reply))}")
    return reply.get("result", {})


def _find_port() -> int:
    alive = json.dumps({"command": "API.IsAlive"}).encode()
    for port in PORTS:
        try:
            if _send(port, alive, timeout=1).get("result", {}).get("isAlive"):
                return port
        except (OSError, ValueError):
            continue
    raise ArchicadError(
        f"No running Archicad found on ports {PORTS.start}-{PORTS.stop - 1}. Open Archicad with a project first."
    )


def _send(port: int, body: bytes, timeout: float = TIMEOUT_SECONDS) -> dict:
    request = urllib.request.Request(
        f"{HOST}:{port}", data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


if __name__ == "__main__":
    mcp.run()
