#!/usr/bin/env python3
"""Google Sheets MCP for Cloud Agent. Credentials via Cursor Secrets env vars."""
import base64
import json
import os
import pickle
import sys
import warnings

warnings.filterwarnings("ignore")

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

CONFIG_DIR = os.environ.get("GWS_CONFIG_DIR", os.path.expanduser("~/.config/gws-aircloset"))
CLIENT_SECRET = os.path.join(CONFIG_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(CONFIG_DIR, "python-credentials.pickle")

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
]


def send(msg):
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _ensure_config_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)

    b64 = os.environ.get("GWS_CREDENTIALS_PICKLE_B64")
    if b64 and not os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "wb") as f:
            f.write(base64.b64decode(b64))

    secret_json = os.environ.get("GWS_CLIENT_SECRET_JSON")
    if secret_json and not os.path.exists(CLIENT_SECRET):
        with open(CLIENT_SECRET, "w", encoding="utf-8") as f:
            f.write(secret_json)


def get_creds():
    _ensure_config_dir()
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_FILE, "wb") as f:
                pickle.dump(creds, f)
        else:
            if not os.path.exists(CLIENT_SECRET):
                raise RuntimeError(
                    "Google Sheets credentials missing. Set Cursor Secret "
                    "GWS_CREDENTIALS_PICKLE_B64 (and optionally GWS_CLIENT_SECRET_JSON)."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=8092, open_browser=False)
            with open(TOKEN_FILE, "wb") as f:
                pickle.dump(creds, f)
    return creds


def sheets_service():
    return build("sheets", "v4", credentials=get_creds(), cache_discovery=False)


def call_tool(name, arguments):
    service = sheets_service()
    if name == "sheets_get":
        req = service.spreadsheets().get(spreadsheetId=arguments["spreadsheetId"])
        if arguments.get("includeGridData"):
            req = service.spreadsheets().get(
                spreadsheetId=arguments["spreadsheetId"], includeGridData=True
            )
        return req.execute()
    if name == "sheets_values_get":
        kwargs = {
            "spreadsheetId": arguments["spreadsheetId"],
            "range": arguments["range"],
        }
        if arguments.get("majorDimension"):
            kwargs["majorDimension"] = arguments["majorDimension"]
        if arguments.get("valueRenderOption"):
            kwargs["valueRenderOption"] = arguments["valueRenderOption"]
        return service.spreadsheets().values().get(**kwargs).execute()
    if name in ("sheets_values_update", "sheets_values_append"):
        values = json.loads(arguments["values"])
        body = {"values": values}
        kwargs = {
            "spreadsheetId": arguments["spreadsheetId"],
            "range": arguments["range"],
            "valueInputOption": arguments.get("valueInputOption", "USER_ENTERED"),
            "body": body,
        }
        if name == "sheets_values_update":
            return service.spreadsheets().values().update(**kwargs).execute()
        return service.spreadsheets().values().append(
            spreadsheetId=arguments["spreadsheetId"],
            range=arguments["range"],
            valueInputOption=arguments.get("valueInputOption", "USER_ENTERED"),
            body=body,
        ).execute()
    raise ValueError(f"Unknown tool: {name}")


def handle(req):
    method = req.get("method")
    rid = req.get("id")
    params = req.get("params") or {}

    if method == "initialize":
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "aircloset-sheets-mcp-cloud", "version": "1.1.0"},
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
            text = json.dumps(result, ensure_ascii=False, indent=2)
            return {"content": [{"type": "text", "text": text}]}
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
