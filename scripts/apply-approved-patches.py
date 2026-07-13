#!/usr/bin/env python3
"""Apply approved WBS patches via gws-python-mcp."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("GWS_CONFIG_DIR", str(Path.home() / ".config/gws-aircloset"))

MCP_PATH = ROOT / "scripts" / "gws-python-mcp.py"
spec = importlib.util.spec_from_file_location("gws_python_mcp", MCP_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)
call_tool = mod.call_tool

SPREADSHEET = "1VaQBMNy2ZCgYs57G2mQWiqof0sTH1umqY4HOjlZBLVE"
SHEET = "新NagiWBS"
ALLOWED = {"D", "E", "G", "H", "I"}


def apply_patch(patch: dict) -> list[str]:
    row = patch["row"]
    updates = patch.get("updates") or {}
    done = []
    for col, val in updates.items():
        if col not in ALLOWED:
            continue
        if val == "" and col != "G":
            continue
        range_a1 = f"{SHEET}!{col}{row}"
        call_tool(
            "sheets_values_update",
            {
                "spreadsheetId": SPREADSHEET,
                "range": range_a1,
                "valueInputOption": "USER_ENTERED",
                "values": json.dumps([[val]], ensure_ascii=False),
            },
        )
        done.append(range_a1)
    return done


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "state/inbox/approved_patches_20260713.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    patches = data["patches"]
    ok, err = [], []
    for p in patches:
        try:
            cells = apply_patch(p)
            ok.append({"row": p["row"], "case_id": p["case_id"], "cells": cells})
            print(f"OK row{p['row']} {p['case_id']} {p['process']}: {cells}")
        except Exception as exc:
            err.append({"row": p["row"], "error": str(exc)})
            print(f"ERR row{p['row']}: {exc}", file=sys.stderr)
    summary = {"updated": len(ok), "errors": len(err), "ok": ok, "err": err}
    out = ROOT / "state" / "apply_result_20260713.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"updated": len(ok), "errors": len(err)}, ensure_ascii=False))
    return 0 if not err else 1


if __name__ == "__main__":
    raise SystemExit(main())
