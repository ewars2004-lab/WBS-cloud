from __future__ import annotations

from wbs_engine.config import WBS_SHEET_NAME
from wbs_engine.models import AuditResult, CellPatch
from wbs_engine.sheets_client import apply_value_patches


def write_approved_patches(audit: AuditResult, dry_run: bool = True) -> dict:
    patches: list[CellPatch] = audit.approved_patches
    if dry_run:
        return {
            "dry_run": True,
            "would_write": len(patches),
            "rows": sorted({p.sheet_row for p in patches}),
        }
    result = apply_value_patches(WBS_SHEET_NAME, patches)
    return {
        "dry_run": False,
        "written": len(patches),
        "api_result": result,
        "rows": sorted({p.sheet_row for p in patches}),
    }
