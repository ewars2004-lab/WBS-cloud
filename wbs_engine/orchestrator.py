from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from wbs_engine.auditor import audit_patches
from wbs_engine.cartographer import build_project_index, parse_wbs_values
from wbs_engine.delta import candidates_to_patches, merge_patches
from wbs_engine.inference import events_to_candidates
from wbs_engine.md_calendar import md_to_wbs_patches, parse_md_grid
from wbs_engine.models import RunReport, SlackEvent
from wbs_engine.reporter import save_run_report
from wbs_engine.sheet_writer import write_approved_patches
from wbs_engine.sheets_client import fetch_md_grid, fetch_wbs_rows, load_fixture
from wbs_engine.slack_events import collect_slack_events, load_events_from_json
from wbs_engine.writer_5w1h import enrich_candidate_patches

JST = timezone(timedelta(hours=9))


def _now_jst() -> str:
    return datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S JST")


def _load_fixture_bundle(name: str) -> dict[str, Any]:
    data = load_fixture(name)
    slack_path = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / name.replace(".json", "_slack.json")
    if slack_path.exists():
        data["slack_events_parsed"] = load_events_from_json(slack_path)
    return data


def run_pipeline(*, dry_run: bool = True, fixture: str | None = None) -> RunReport:
    run_id = datetime.now(JST).strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
    report = RunReport(run_id=run_id)

    first_row = 6
    if fixture:
        data = _load_fixture_bundle(fixture)
        wbs_values = data["wbs_values"]
        md_values = data.get("values", [])
        md_grid = data.get("grid", [])
        slack_events: list[SlackEvent] = data.get("slack_events_parsed", [])
        first_row = int(data.get("wbs_first_row", 6))
    else:
        wbs_values = fetch_wbs_rows()
        md_data = fetch_md_grid()
        if wbs_values is None:
            raise RuntimeError("WBSシートを読めません。MCP_SETUP.md を参照してください。")
        md_values, md_grid = md_data if md_data else ([], [])
        slack_events = collect_slack_events()

    rows = parse_wbs_values(wbs_values, first_row=first_row)
    rows_by_num = {r.sheet_row: r for r in rows}
    project_index = build_project_index(rows)

    md_patches = []
    if md_grid and md_values:
        deadlines = parse_md_grid(md_grid, md_values)
        md_patches = md_to_wbs_patches(deadlines, rows)
        report.md_sync_count = len([p for p in md_patches if p.column == "due"])

    candidates = events_to_candidates(slack_events, project_index)
    slack_patches = candidates_to_patches(candidates)
    for cand in candidates:
        row = rows_by_num.get(cand.sheet_row)
        if row:
            slack_patches.extend(enrich_candidate_patches(cand, row))

    all_patches = merge_patches(md_patches, slack_patches)
    audit = audit_patches(all_patches, rows_by_num)
    report.audit_issues = audit.issues
    report.skipped = [
        {"tier": i.tier, "code": i.code, "message": i.message, "row": i.patch.sheet_row if i.patch else None}
        for i in audit.issues
    ]

    if audit.passed:
        write_result = write_approved_patches(audit, dry_run=dry_run)
        report.updated_rows = write_result.get("rows", [])
    else:
        report.skipped.append({"tier": "blocked", "code": "AUDITOR_FAIL", "message": "書込停止"})

    return report


def report_to_markdown(report: RunReport, *, dry_run: bool) -> str:
    tier_c = [i for i in report.audit_issues if i.tier == "C"]
    lines = [
        f"## WBS更新チーム — Run {report.run_id}",
        "",
        f"- 実行時刻: {_now_jst()}",
        f"- モード: {'dry-run' if dry_run else 'apply'}",
        f"- MD同期(F列): {report.md_sync_count}件",
        f"- 更新行: {report.updated_rows or 'なし'}",
        f"- Auditor: {'PASS' if not tier_c else 'FAIL'}",
    ]
    if report.skipped:
        lines.append("- 見送り/ブロック:")
        for s in report.skipped[:20]:
            lines.append(f"  - {s}")
    return "\n".join(lines)


def execute_run(*, dry_run: bool = True, fixture: str | None = None) -> dict:
    report = run_pipeline(dry_run=dry_run, fixture=fixture)
    md = report_to_markdown(report, dry_run=dry_run)
    path = save_run_report(report, md)
    return {
        "run_id": report.run_id,
        "report_path": str(path),
        "markdown": md,
        "md_sync_count": report.md_sync_count,
        "updated_rows": report.updated_rows,
        "audit_passed": not any(i.tier == "C" for i in report.audit_issues),
        "dry_run": dry_run,
    }
