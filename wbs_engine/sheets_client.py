from __future__ import annotations

import json
import os
import pickle
import sys
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from wbs_engine.config import (
    MD_SHEET_NAME,
    MD_SPREADSHEET_ID,
    REPO_ROOT,
    WBS_FIRST_TASK_ROW,
    WBS_SHEET_NAME,
    WBS_SPREADSHEET_ID,
)

COL_LETTERS = {
    "project": "A",
    "action": "B",
    "estimate": "C",
    "next_action": "D",
    "state": "E",
    "due": "F",
    "completed_at": "G",
    "evidence": "H",
    "memo": "I",
    "when": "J",
    "where": "K",
    "who": "L",
    "what": "M",
    "why": "N",
    "how": "O",
}


def credentials_path() -> Path:
    env = os.environ.get("GOOGLE_CREDENTIALS_PATH", "").strip()
    if env:
        return Path(env).expanduser()
    return Path.home() / ".config/gws-aircloset/python-credentials.pickle"


def get_sheets_service():
    cred_path = credentials_path()
    if not cred_path.exists():
        return None
    with cred_path.open("rb") as fh:
        creds = pickle.load(fh)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("sheets", "v4", credentials=creds)


def fetch_values(spreadsheet_id: str, range_a1: str) -> list[list[str]] | None:
    svc = get_sheets_service()
    if not svc:
        return None
    resp = svc.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_a1).execute()
    return resp.get("values", [])


def fetch_grid(spreadsheet_id: str, sheet_name: str, max_row: int = 200) -> tuple[list[list[str]], list[list[dict]]] | None:
    svc = get_sheets_service()
    if not svc:
        return None
    meta = (
        svc.spreadsheets()
        .get(
            spreadsheetId=spreadsheet_id,
            includeGridData=True,
            ranges=[f"{sheet_name}!A1:ZZ{max_row}"],
        )
        .execute()
    )
    sheet = meta["sheets"][0]
    grid = sheet.get("data", [{}])[0].get("rowData", [])
    values: list[list[str]] = []
    grid_cells: list[list[dict]] = []
    for row in grid:
        cells = row.get("values", [])
        grid_cells.append(cells)
        values.append([c.get("formattedValue", "") for c in cells])
    return values, grid_cells


def fetch_wbs_rows(max_row: int = 500) -> list[list[str]] | None:
    return fetch_values(WBS_SPREADSHEET_ID, f"{WBS_SHEET_NAME}!A{WBS_FIRST_TASK_ROW}:O{max_row}")


def fetch_md_grid() -> tuple[list[list[str]], list[list[dict]]] | None:
    return fetch_grid(MD_SPREADSHEET_ID, MD_SHEET_NAME)


def patch_to_a1(sheet_name: str, sheet_row: int, column: str) -> str:
    letter = COL_LETTERS.get(column, column.upper())
    return f"{sheet_name}!{letter}{sheet_row}"


def apply_value_patches(sheet_name: str, patches: list, spreadsheet_id: str = WBS_SPREADSHEET_ID) -> dict[str, Any]:
    svc = get_sheets_service()
    if not svc:
        raise RuntimeError("Google Sheets に接続できません。MCP_SETUP.md を参照してください。")

    data = []
    for patch in patches:
        data.append(
            {
                "range": patch_to_a1(sheet_name, patch.sheet_row, patch.column),
                "values": [[patch.new_value]],
            }
        )
    if not data:
        return {"updatedCells": 0, "updatedRows": 0}

    body = {"valueInputOption": "USER_ENTERED", "data": data}
    return svc.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()


def load_fixture(name: str) -> Any:
    path = REPO_ROOT / "tests" / "fixtures" / name
    return json.loads(path.read_text(encoding="utf-8"))
