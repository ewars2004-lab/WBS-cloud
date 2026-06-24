#!/usr/bin/env python3
"""Sheets read/write CLI for Cloud Agent when stdio MCP is unavailable."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MCP_PATH = ROOT / "gws-python-mcp.py"
DEFAULT_PROFILE_DIR = Path.home() / ".config/gws-aircloset"


def _load_mcp():
    import os

    os.environ.setdefault("GWS_CONFIG_DIR", str(DEFAULT_PROFILE_DIR))
    spec = importlib.util.spec_from_file_location("gws_python_mcp", MCP_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {MCP_PATH}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    parser = argparse.ArgumentParser(description="Google Sheets CLI (WBS-cloud fallback)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    get_p = sub.add_parser("values-get", help="Read a range")
    get_p.add_argument("--spreadsheet", required=True)
    get_p.add_argument("--range", required=True)
    get_p.add_argument("--major-dimension", default="")
    get_p.add_argument("--value-render-option", default="")

    upd_p = sub.add_parser("values-update", help="Write a range")
    upd_p.add_argument("--spreadsheet", required=True)
    upd_p.add_argument("--range", required=True)
    upd_p.add_argument("--values", required=True, help="2D JSON array string")
    upd_p.add_argument("--value-input-option", default="USER_ENTERED")

    app_p = sub.add_parser("values-append", help="Append to a range")
    app_p.add_argument("--spreadsheet", required=True)
    app_p.add_argument("--range", required=True)
    app_p.add_argument("--values", required=True, help="2D JSON array string")
    app_p.add_argument("--value-input-option", default="USER_ENTERED")

    sub.add_parser("verify", help="Smoke test: read 新NagiWBS header row")

    args = parser.parse_args()
    mcp = _load_mcp()

    try:
        if args.cmd == "verify":
            result = mcp.call_tool(
                "sheets_values_get",
                {
                    "spreadsheetId": "1VaQBMNy2ZCgYs57G2mQWiqof0sTH1umqY4HOjlZBLVE",
                    "range": "新NagiWBS!A5:O5",
                },
            )
        elif args.cmd == "values-get":
            payload = {"spreadsheetId": args.spreadsheet, "range": args.range}
            if args.major_dimension:
                payload["majorDimension"] = args.major_dimension
            if args.value_render_option:
                payload["valueRenderOption"] = args.value_render_option
            result = mcp.call_tool("sheets_values_get", payload)
        elif args.cmd == "values-update":
            result = mcp.call_tool(
                "sheets_values_update",
                {
                    "spreadsheetId": args.spreadsheet,
                    "range": args.range,
                    "valueInputOption": args.value_input_option,
                    "values": args.values,
                },
            )
        else:
            result = mcp.call_tool(
                "sheets_values_append",
                {
                    "spreadsheetId": args.spreadsheet,
                    "range": args.range,
                    "valueInputOption": args.value_input_option,
                    "values": args.values,
                },
            )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
