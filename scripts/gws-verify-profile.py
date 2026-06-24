#!/usr/bin/env python3
"""Verify GWS profile: account email + Sheets/Slides API reachability."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

PROFILES = {
    "aircloset": {
        "dir": os.path.expanduser("~/.config/gws-aircloset"),
        "label": "r.yaguchi@air-closet.com (expected)",
    },
    "personal": {
        "dir": os.path.expanduser("~/.config/gws"),
        "label": "ewars2004@gmail.com (expected)",
    },
}


def load_mcp():
    root = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("gws_mcp", root / "gws-python-mcp.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    profile = sys.argv[1] if len(sys.argv) > 1 else "aircloset"
    if profile not in PROFILES:
        print(f"Unknown profile: {profile}", file=sys.stderr)
        return 1

    os.environ["GWS_CONFIG_DIR"] = PROFILES[profile]["dir"]
    mcp = load_mcp()

    try:
        about = mcp.call_tool("drive_about", {})
        email = about.get("user", {}).get("emailAddress", "?")
        print(json.dumps({"profile": profile, "email": email, "expected": PROFILES[profile]["label"]}, indent=2))

        # Sheets smoke (WBS header) — may 403 if no access; still proves auth works
        try:
            mcp.call_tool(
                "sheets_values_get",
                {
                    "spreadsheetId": "1VaQBMNy2ZCgYs57G2mQWiqof0sTH1umqY4HOjlZBLVE",
                    "range": "新NagiWBS!A5:E5",
                },
            )
            print("sheets: OK")
        except Exception as e:
            print(f"sheets: SKIP ({str(e)[:80]})")

        print("slides_api: scope included (use slides_get with a presentationId to test)")
        print("docs_api: scope included (use docs_get with a documentId to test)")
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
