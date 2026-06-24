#!/usr/bin/env python3
"""Google Workspace MCP (Sheets, Slides, Docs, Drive) via Python OAuth.

Set GWS_CONFIG_DIR to credential directory, e.g.:
  ~/.config/gws-aircloset  (r.yaguchi@air-closet.com)
  ~/.config/gws            (ewars2004@gmail.com)

Cloud Agent: Dashboard Secrets に
  GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET / GWS_CREDENTIALS_PICKLE_B64_PERSONAL
を登録。cloud-install.sh が pickle を展開する。
"""
from __future__ import annotations

import base64
import json
import os
import pickle
import sys
import warnings

warnings.filterwarnings("ignore")

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from gws_credentials import config_dir as gws_config_dir, pickle_b64_from_environ, profile_key

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/calendar",
]

CONFIG_DIR = str(gws_config_dir())
CLIENT_SECRET = os.path.join(CONFIG_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(CONFIG_DIR, "python-credentials.pickle")
OAUTH_PORT = int(os.environ.get("GWS_OAUTH_PORT", "8092"))
PROFILE = profile_key()

TOOLS = [
    {
        "name": "sheets_get",
        "description": "Get spreadsheet metadata.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "spreadsheetId": {"type": "string"},
                "includeGridData": {"type": "boolean"},
            },
            "required": ["spreadsheetId"],
        },
    },
    {
        "name": "sheets_values_get",
        "description": "Read values from a spreadsheet range.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "spreadsheetId": {"type": "string"},
                "range": {"type": "string"},
                "majorDimension": {"type": "string"},
                "valueRenderOption": {"type": "string"},
            },
            "required": ["spreadsheetId", "range"],
        },
    },
    {
        "name": "sheets_values_update",
        "description": "Write values to a spreadsheet range.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "spreadsheetId": {"type": "string"},
                "range": {"type": "string"},
                "valueInputOption": {"type": "string"},
                "values": {"type": "string", "description": "2D JSON array string"},
            },
            "required": ["spreadsheetId", "range", "valueInputOption", "values"],
        },
    },
    {
        "name": "sheets_values_append",
        "description": "Append values to a spreadsheet range.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "spreadsheetId": {"type": "string"},
                "range": {"type": "string"},
                "valueInputOption": {"type": "string"},
                "values": {"type": "string", "description": "2D JSON array string"},
            },
            "required": ["spreadsheetId", "range", "valueInputOption", "values"],
        },
    },
    {
        "name": "slides_get",
        "description": "Get Google Slides presentation metadata and slide content.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "presentationId": {"type": "string"},
            },
            "required": ["presentationId"],
        },
    },
    {
        "name": "slides_create",
        "description": "Create a blank Google Slides presentation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
            },
            "required": ["title"],
        },
    },
    {
        "name": "docs_get",
        "description": "Get Google Doc content (plain text).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "documentId": {"type": "string"},
            },
            "required": ["documentId"],
        },
    },
    {
        "name": "drive_about",
        "description": "Get authenticated user email (which Google account this MCP uses).",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def send(msg):
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _load_pickle_b64() -> bytes | None:
    b64 = pickle_b64_from_environ()
    if not b64:
        return None
    return base64.b64decode(b64)


def get_creds():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    creds = None

    raw = _load_pickle_b64()
    if raw:
        creds = pickle.loads(raw)
    elif os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                creds = None
        if not creds or not creds.valid:
            if not os.path.exists(CLIENT_SECRET):
                raise RuntimeError(
                    f"Missing {CLIENT_SECRET}. Run: scripts/gws-oauth-login.sh {PROFILE}"
                )
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=OAUTH_PORT, open_browser=True)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
    return creds


def call_tool(name, arguments):
    creds = get_creds()
    args = arguments or {}

    if name == "drive_about":
        svc = build("drive", "v3", credentials=creds, cache_discovery=False)
        return svc.about().get(fields="user").execute()

    if name.startswith("sheets_"):
        svc = build("sheets", "v4", credentials=creds, cache_discovery=False)
        if name == "sheets_get":
            req = svc.spreadsheets().get(spreadsheetId=args["spreadsheetId"])
            if args.get("includeGridData"):
                req = svc.spreadsheets().get(
                    spreadsheetId=args["spreadsheetId"], includeGridData=True
                )
            return req.execute()
        if name == "sheets_values_get":
            kwargs = {"spreadsheetId": args["spreadsheetId"], "range": args["range"]}
            if args.get("majorDimension"):
                kwargs["majorDimension"] = args["majorDimension"]
            if args.get("valueRenderOption"):
                kwargs["valueRenderOption"] = args["valueRenderOption"]
            return svc.spreadsheets().values().get(**kwargs).execute()
        if name in ("sheets_values_update", "sheets_values_append"):
            values = json.loads(args["values"])
            body = {"values": values}
            kwargs = {
                "spreadsheetId": args["spreadsheetId"],
                "range": args["range"],
                "valueInputOption": args.get("valueInputOption", "USER_ENTERED"),
                "body": body,
            }
            if name == "sheets_values_update":
                return svc.spreadsheets().values().update(**kwargs).execute()
            return svc.spreadsheets().values().append(
                spreadsheetId=args["spreadsheetId"],
                range=args["range"],
                valueInputOption=args.get("valueInputOption", "USER_ENTERED"),
                body=body,
            ).execute()

    if name.startswith("slides_"):
        svc = build("slides", "v1", credentials=creds, cache_discovery=False)
        if name == "slides_get":
            return svc.presentations().get(presentationId=args["presentationId"]).execute()
        if name == "slides_create":
            return svc.presentations().create(body={"title": args["title"]}).execute()

    if name == "docs_get":
        svc = build("docs", "v1", credentials=creds, cache_discovery=False)
        return svc.documents().get(documentId=args["documentId"]).execute()

    raise ValueError(f"Unknown tool: {name}")


def handle(req):
    method = req.get("method")
    rid = req.get("id")
    params = req.get("params") or {}

    if method == "initialize":
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": f"gws-python-mcp-{PROFILE}", "version": "2.0.0"},
        }
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return {"tools": TOOLS}
    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}
        try:
            result = call_tool(name, arguments)
            return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": str(e)}], "isError": True}
    if method == "ping":
        return {}
    if rid is not None:
        raise ValueError(f"Unsupported method: {method}")
    return None


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        req = json.loads(line)
        rid = req.get("id")
        try:
            result = handle(req)
            if rid is None:
                continue
            send({"jsonrpc": "2.0", "id": rid, "result": result})
        except Exception as e:
            if rid is not None:
                send({"jsonrpc": "2.0", "id": rid, "error": {"code": -32000, "message": str(e)}})


if __name__ == "__main__":
    main()
