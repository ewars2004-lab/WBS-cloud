from __future__ import annotations

import json
from pathlib import Path

from wbs_engine.config import STATE_DIR


def save_run_report(report, markdown: str) -> Path:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    path = STATE_DIR / "last_run.json"
    payload = {
        "last_run_id": report.run_id,
        "last_run_at": markdown.split("\n")[2].replace("- 実行時刻: ", "") if markdown else None,
        "md_sync_count": report.md_sync_count,
        "updated_rows": report.updated_rows,
        "skipped_count": len(report.skipped),
        "audit_tier_c": len([i for i in report.audit_issues if i.tier == "C"]),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    report_path = STATE_DIR / f"run_{report.run_id}.md"
    report_path.write_text(markdown, encoding="utf-8")
    return report_path
