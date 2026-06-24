#!/usr/bin/env python3
"""Merge dual GWS MCP servers into ~/.cursor/mcp.json without removing others."""
from __future__ import annotations

import json
import os
from pathlib import Path

HOME = Path.home()
MCP_JSON = HOME / ".cursor" / "mcp.json"
BIN = HOME / ".local" / "bin"

GWS_SERVERS = {
    "google-workspace-aircloset": {
        "command": str(BIN / "aircloset-gws-mcp"),
        "args": [],
        "env": {"GWS_CONFIG_DIR": str(HOME / ".config/gws-aircloset")},
    },
    "google-workspace-personal": {
        "command": str(BIN / "personal-gws-mcp"),
        "args": [],
        "env": {"GWS_CONFIG_DIR": str(HOME / ".config/gws")},
    },
}


def main() -> int:
    MCP_JSON.parent.mkdir(parents=True, exist_ok=True)
    data: dict = {"mcpServers": {}}
    if MCP_JSON.is_file():
        data = json.loads(MCP_JSON.read_text(encoding="utf-8"))
    servers = data.setdefault("mcpServers", {})
    for name, cfg in GWS_SERVERS.items():
        servers[name] = cfg
    MCP_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"✅ updated {MCP_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
