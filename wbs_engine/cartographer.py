from __future__ import annotations

import re

from wbs_engine.config import COL, WBS_FIRST_TASK_ROW
from wbs_engine.models import RowKind, WbsRow


def _cell(row: list[str], col: int) -> str:
    if col < len(row):
        return str(row[col]).strip()
    return ""


def classify_row(project: str, action: str) -> RowKind:
    if project and not action:
        if project.startswith("MD関連"):
            return RowKind.MD_HEADER
        if project.startswith("AIRCLOSET-"):
            return RowKind.PROJECT_HEADER
        return RowKind.PROJECT_HEADER
    if project and action:
        if "：" in project or action in {"MDを期日入れる", "計画作成", "FB", "修正", "修正FB", "転記"}:
            if project.startswith("MD") and action == "MDを期日入れる":
                return RowKind.MD_BRAND
            if "：" in project:
                return RowKind.MD_BRAND
        return RowKind.TASK
    return RowKind.OTHER


def parse_wbs_values(values: list[list[str]], first_row: int = WBS_FIRST_TASK_ROW) -> list[WbsRow]:
    rows: list[WbsRow] = []
    for idx, raw in enumerate(values):
        sheet_row = first_row + idx
        project = _cell(raw, COL["project"])
        action = _cell(raw, COL["action"])
        if not project and not action:
            continue
        rows.append(
            WbsRow(
                sheet_row=sheet_row,
                kind=classify_row(project, action),
                project=project,
                action=action,
                estimate=_cell(raw, COL["estimate"]),
                next_action=_cell(raw, COL["next_action"]),
                state=_cell(raw, COL["state"]),
                due=_cell(raw, COL["due"]),
                completed_at=_cell(raw, COL["completed_at"]),
                evidence=_cell(raw, COL["evidence"]),
                memo=_cell(raw, COL["memo"]),
                when=_cell(raw, COL["when"]),
                where=_cell(raw, COL["where"]),
                who=_cell(raw, COL["who"]),
                what=_cell(raw, COL["what"]),
                why=_cell(raw, COL["why"]),
                how=_cell(raw, COL["how"]),
            )
        )
    return rows


def build_project_index(rows: list[WbsRow]) -> dict[str, list[WbsRow]]:
    index: dict[str, list[WbsRow]] = {}
    current = ""
    for row in rows:
        if row.kind in {RowKind.PROJECT_HEADER, RowKind.MD_HEADER}:
            current = row.project
        if current:
            index.setdefault(current, []).append(row)
    return index


def extract_project_keys(text: str) -> list[str]:
    keys: list[str] = []
    for m in re.finditer(r"AIRCLOSET-(\d+)", text, re.I):
        keys.append(f"AIRCLOSET-{m.group(1)}")
    for m in re.finditer(r"pj[_-]?(\d+)", text, re.I):
        keys.append(f"pj_{m.group(1)}")
    return list(dict.fromkeys(keys))


def find_channel_name(project_key: str) -> str:
    m = re.search(r"AIRCLOSET-(\d+)", project_key, re.I)
    if not m:
        return ""
    return f"#pj_{m.group(1)}_"


def open_tasks(rows: list[WbsRow]) -> list[WbsRow]:
    return [r for r in rows if r.kind == RowKind.TASK and r.state != "完了"]


def md_brand_rows(rows: list[WbsRow]) -> list[WbsRow]:
    return [r for r in rows if r.is_md_brand_row and r.action != "MDを期日入れる"]
