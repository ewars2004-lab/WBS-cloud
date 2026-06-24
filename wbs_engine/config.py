from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DICT_DIR = REPO_ROOT / "dict"
STATE_DIR = REPO_ROOT / "state"

WBS_SPREADSHEET_ID = "1VaQBMNy2ZCgYs57G2mQWiqof0sTH1umqY4HOjlZBLVE"
WBS_SHEET_NAME = "新NagiWBS"
WBS_GID = 2026060205
WBS_FIRST_TASK_ROW = 6

MD_SPREADSHEET_ID = "1x9urTyDl_obuvbTCJVj3FlpYNFljRZNS6XdZcMOw2TQ"
MD_SHEET_NAME = "BSOMDスケジュール"
MD_GID = 394259552

COL = {
    "project": 0,
    "action": 1,
    "estimate": 2,
    "next_action": 3,
    "state": 4,
    "due": 5,
    "completed_at": 6,
    "evidence": 7,
    "memo": 8,
    "when": 9,
    "where": 10,
    "who": 11,
    "what": 12,
    "why": 13,
    "how": 14,
}

VALID_STATES = frozenset({"完了", "未着手", "進行中"})
F_EDIT_ALLOWED_PREFIXES = ("MD", "NOLLEYS", "UNFILO", "SNIDEL", "Mila Owen", "humanwoman", "MARKSTYLER", "NBB", "ROPE", "FRAY", "nano", "NATURAL", "ONWARD", "BANYARD", "COLLAGE", "JILL", "PROPORTION")

NAGI_SLACK_IDS = ("U08QC76DQRH", "r.yaguchi", "Nagi")
DEFAULT_LOOKBACK = "2026-05-01"


def load_json(name: str) -> dict:
    path = DICT_DIR / name
    return json.loads(path.read_text(encoding="utf-8"))
