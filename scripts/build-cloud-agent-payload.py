#!/usr/bin/env python3
"""Build Cloud Agents API launch payload for WBS-cloud (stdout JSON)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCAL = ROOT / ".local"
SECRET_AIRCLOSET = LOCAL / "GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET.txt"
SECRET_PERSONAL = LOCAL / "GWS_CREDENTIALS_PICKLE_B64_PERSONAL.txt"
ONE_SHOT = ROOT / "docs" / "CLOUD_AGENT_ONE_SHOT.md"
VERIFY_PROMPT = """AGENTS.md を読み、次を実行して結果を報告してください:

bash scripts/cloud-install.sh
bash scripts/verify-cloud-ready.sh
"""
SLACK_CLIENT_ID = "3660753192626.8903469228982"
REPO_URL = "https://github.com/ewars2004-lab/WBS-cloud"


def _read_secret(path: Path, label: str) -> str:
    if not path.is_file():
        print(f"ERROR: missing {path}. Run: bash scripts/prepare-dual-secrets.sh", file=sys.stderr)
        raise SystemExit(1)
    return path.read_text(encoding="utf-8").strip()


def main() -> int:
    b64_aircloset = _read_secret(SECRET_AIRCLOSET, "aircloset")
    b64_personal = _read_secret(SECRET_PERSONAL, "personal")

    prompt = ONE_SHOT.read_text(encoding="utf-8") if ONE_SHOT.is_file() else VERIFY_PROMPT
    if os.environ.get("WBS_CLOUD_VERIFY_ONLY", "1") == "1":
        prompt = VERIFY_PROMPT

    home = "/home/ubuntu"
    payload = {
        "prompt": {"text": prompt},
        "model": {"id": "composer-2"},
        "repos": [{"url": REPO_URL, "startingRef": "main"}],
        "envVars": {
            "GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET": b64_aircloset,
            "GWS_CREDENTIALS_PICKLE_B64_PERSONAL": b64_personal,
        },
        "mcpServers": [
            {
                "name": "slack",
                "type": "http",
                "url": "https://mcp.slack.com/mcp",
                "auth": {"CLIENT_ID": SLACK_CLIENT_ID},
            },
            {
                "name": "google-workspace-aircloset",
                "type": "stdio",
                "command": "python3",
                "args": ["scripts/gws-python-mcp.py"],
                "env": {
                    "GWS_CONFIG_DIR": f"{home}/.config/gws-aircloset",
                    "GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET": b64_aircloset,
                },
            },
            {
                "name": "google-workspace-personal",
                "type": "stdio",
                "command": "python3",
                "args": ["scripts/gws-python-mcp.py"],
                "env": {
                    "GWS_CONFIG_DIR": f"{home}/.config/gws",
                    "GWS_CREDENTIALS_PICKLE_B64_PERSONAL": b64_personal,
                },
            },
        ],
    }
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
