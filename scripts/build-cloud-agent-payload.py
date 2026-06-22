#!/usr/bin/env python3
"""Build Cloud Agents API launch payload for WBS-cloud (stdout JSON)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECRET_FILE = ROOT / ".local" / "GWS_CREDENTIALS_PICKLE_B64.txt"
ONE_SHOT = ROOT / "docs" / "CLOUD_AGENT_ONE_SHOT.md"
SLACK_CLIENT_ID = "3660753192626.8903469228982"
REPO_URL = "https://github.com/ewars2004-lab/WBS-cloud"


def main() -> int:
    if not SECRET_FILE.is_file():
        print(f"ERROR: missing {SECRET_FILE}. Run ./scripts/setup-cloud-complete.sh first.", file=sys.stderr)
        return 1

    b64 = SECRET_FILE.read_text(encoding="utf-8").strip()
    prompt = ONE_SHOT.read_text(encoding="utf-8") if ONE_SHOT.is_file() else (
        "AGENTS.md と skills/wbs-update-workflow を読み、WBS更新チームでバッチ実行してください。"
    )

    payload = {
        "prompt": {"text": prompt},
        "model": {"id": "composer-2"},
        "repos": [{"url": REPO_URL, "startingRef": "main"}],
        "envVars": {"GWS_CREDENTIALS_PICKLE_B64": b64},
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
                "args": ["scripts/aircloset-sheets-mcp-cloud.py"],
                "env": {"GWS_CREDENTIALS_PICKLE_B64": b64},
            },
        ],
    }
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
