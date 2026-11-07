# Archicad MCP

Lets AI agents (Claude Desktop, Claude Code, Codex CLI) read and change a running Archicad project.
Works with Archicad 25 and newer (tested target: Archicad 29), on Mac and Windows.

It gives the agent two tools:

- `archicad_command`: any built-in Archicad JSON API command (list elements, read/write properties, classifications, ...).
- `tapir_command`: any [Tapir](https://github.com/ENZYME-APD/tapir-archicad-automation) add-on command (create/move/delete elements, story info, publishing, ...). Only needed if you want the agent to create or move things.

## 1. Install uv (one time)

`uv` runs the script and installs its Python dependency automatically.

- Mac: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

Then find its full path (you need it below):

- Mac: `which uv` (usually `/Users/<you>/.local/bin/uv`)
- Windows: `where uv` (usually `C:\Users\<you>\.local\bin\uv.exe`)

Put `archicad_mcp.py` somewhere permanent, e.g. `~/archicad-mcp/archicad_mcp.py`.

## 2. Optional: install Tapir

Download the Tapir release for Archicad 29 from
https://github.com/ENZYME-APD/tapir-archicad-automation/releases, then in Archicad:
Options > Add-On Manager > Add, and pick the downloaded add-on file. Restart Archicad.

## 3. Connect Claude

### Claude Desktop

Open Settings > Developer > Edit Config. That opens `claude_desktop_config.json`
(Mac: `~/Library/Application Support/Claude/`, Windows: `%APPDATA%\Claude\`). Add:

```json
{
  "mcpServers": {
    "archicad": {
      "command": "/Users/<you>/.local/bin/uv",
      "args": ["run", "/Users/<you>/archicad-mcp/archicad_mcp.py"]
    }
  }
}
```

On Windows use the Windows paths with double backslashes, e.g.
`"C:\\Users\\<you>\\.local\\bin\\uv.exe"`. If the file already has an `mcpServers` block, add the
`"archicad"` entry inside it. Fully quit and reopen Claude Desktop.

### Codex CLI

```
codex mcp add archicad -- uv run /Users/<you>/archicad-mcp/archicad_mcp.py
```

### Claude Code

```
claude mcp add archicad --scope user -- uv run /Users/<you>/archicad-mcp/archicad_mcp.py
```

## 4. Use it

1. Open Archicad with a project. It must stay open while the agent works.
2. Ask the agent, for example: "Use Archicad to list all walls and their Element IDs" or
   "Set the Renovation Status of all selected doors to New".

If it says "No running Archicad found", Archicad is closed or no project is open.

Save a copy of the project before letting an agent edit a real one.

## Self-check without Archicad

Runs the tools against a fake Archicad on localhost:

```
uv run --with "mcp>=2.3,<3" python test_archicad_mcp.py
```

Prints `ok` on success.


[![M8ven Score](https://m8ven.ai/badge/mcp/petarstoev02-archicad-mcp-3ntqk1?v=ed46d4c659a00811bcc0360390ad104d)](https://m8ven.ai/mcp/petarstoev02-archicad-mcp-3ntqk1?s=readme)
