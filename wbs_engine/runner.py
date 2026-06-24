from __future__ import annotations

import json
import sys

from wbs_engine.config import REPO_ROOT
from wbs_engine.orchestrator import execute_run
from wbs_engine.reporter import save_run_report
from wbs_engine.sheets_client import credentials_path, fetch_wbs_rows
from wbs_engine.cartographer import md_brand_rows, parse_wbs_values
from wbs_engine.auditor import audit_patches
from wbs_engine.md_calendar import md_to_wbs_patches, parse_md_grid
from wbs_engine.sheets_client import fetch_md_grid


def cmd_cartographer() -> int:
    values = fetch_wbs_rows()
    if values is None:
        print("ERROR: Google Sheets に接続できません。MCP_SETUP.md を参照してください。", file=sys.stderr)
        return 1
    rows = parse_wbs_values(values)
    print(
        json.dumps(
            {
                "task_rows": len(rows),
                "open": len([r for r in rows if r.state != "完了"]),
                "md_brands": len(md_brand_rows(rows)),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def cmd_md_sync(dry_run: bool = True) -> int:
    wbs_values = fetch_wbs_rows()
    md_data = fetch_md_grid()
    if wbs_values is None or md_data is None:
        print("ERROR: Sheets接続失敗", file=sys.stderr)
        return 1
    md_values, md_grid = md_data
    wbs_rows = parse_wbs_values(wbs_values)
    deadlines = parse_md_grid(md_grid, md_values)
    patches = md_to_wbs_patches(deadlines, wbs_rows)
    rows_by_num = {r.sheet_row: r for r in wbs_rows}
    audit = audit_patches(patches, rows_by_num)
    report = {
        "deadlines_found": len(deadlines),
        "patches_proposed": len(patches),
        "audit_passed": audit.passed,
        "issues": [{"tier": i.tier, "code": i.code, "message": i.message} for i in audit.issues],
        "approved": [
            {"row": p.sheet_row, "col": p.column, "new": p.new_value, "reason": p.reason}
            for p in audit.approved_patches
        ],
        "dry_run": dry_run,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if audit.passed or dry_run else 1


def cmd_run(dry_run: bool = True, fixture: str | None = None) -> int:
    try:
        result = execute_run(dry_run=dry_run, fixture=fixture)
    except RuntimeError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps({k: v for k, v in result.items() if k != "markdown"}, ensure_ascii=False, indent=2))
    print("\n" + result["markdown"])
    tier_fail = not result["audit_passed"]
    return 1 if tier_fail and not dry_run else 0


def cmd_validate() -> int:
    from tests import run_self_check

    return run_self_check()


def cmd_doctor() -> int:
    from pathlib import Path

    skills = Path.home() / ".cursor/skills/wbs-workflow"
    inbox = REPO_ROOT / "state/inbox"
    print(
        json.dumps(
            {
                "repo": str(REPO_ROOT),
                "gws_credentials": credentials_path().exists(),
                "gws_credentials_path": str(credentials_path()),
                "skill_linked": skills.is_symlink() or skills.exists(),
                "inbox_events": len(list(inbox.glob("*.json"))) if inbox.exists() else 0,
                "slack_token": bool(__import__("os").environ.get("SLACK_BOT_TOKEN")),
            },
            indent=2,
        )
    )
    return 0


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="WBS更新チーム CLI")
    parser.add_argument(
        "command",
        choices=["cartographer", "md-sync", "run", "validate", "doctor"],
    )
    parser.add_argument("--apply", action="store_true", help="シートへ実際に書き込む")
    parser.add_argument("--fixture", help="tests/fixtures 内のJSONでオフライン実行")
    args = parser.parse_args()

    dry_run = not args.apply

    if args.command == "cartographer":
        raise SystemExit(cmd_cartographer())
    if args.command == "md-sync":
        raise SystemExit(cmd_md_sync(dry_run=dry_run))
    if args.command == "run":
        raise SystemExit(cmd_run(dry_run=dry_run, fixture=args.fixture))
    if args.command == "validate":
        raise SystemExit(cmd_validate())
    if args.command == "doctor":
        raise SystemExit(cmd_doctor())


if __name__ == "__main__":
    main()
