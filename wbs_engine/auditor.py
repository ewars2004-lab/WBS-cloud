from __future__ import annotations

import re
from datetime import datetime

from wbs_engine.config import COL, VALID_STATES, load_json
from wbs_engine.models import AuditIssue, AuditResult, CellPatch, Confidence, WbsRow


def _tier_c(code: str, message: str, patch: CellPatch | None = None) -> AuditIssue:
    return AuditIssue(tier="C", code=code, message=message, patch=patch)


def _tier_b(code: str, message: str, patch: CellPatch | None = None) -> AuditIssue:
    return AuditIssue(tier="B", code=code, message=message, patch=patch)


def audit_patches(patches: list[CellPatch], rows_by_number: dict[int, WbsRow]) -> AuditResult:
    issues: list[AuditIssue] = []
    approved: list[CellPatch] = []

    for patch in patches:
        row = rows_by_number.get(patch.sheet_row)
        if patch.column == "due":
            if not row or not row.allows_f_edit:
                issues.append(
                    _tier_c(
                        "F_FORBIDDEN",
                        f"行{patch.sheet_row}: F列(完了期限)はMDブランド行以外では編集禁止",
                        patch,
                    )
                )
                continue

        if patch.column == "state":
            if patch.new_value not in VALID_STATES:
                issues.append(
                    _tier_c("INVALID_STATE", f"行{patch.sheet_row}: 状態は {sorted(VALID_STATES)} のみ", patch)
                )
                continue
            if patch.new_value == "完了":
                evidence_patch = next(
                    (p for p in patches if p.sheet_row == patch.sheet_row and p.column == "evidence"),
                    None,
                )
                has_evidence = bool(evidence_patch and evidence_patch.new_value) or bool(row and row.evidence)
                if not has_evidence and patch.confidence != Confidence.HIGH:
                    issues.append(
                        _tier_b(
                            "MISSING_EVIDENCE",
                            f"行{patch.sheet_row}: 完了にはH列(Slack根拠)が必要",
                            patch,
                        )
                    )
                    continue

        if patch.column == "project" and patch.new_value == "":
            issues.append(_tier_c("DELETE_ROW", f"行{patch.sheet_row}: 行削除・空行化は禁止", patch))
            continue

        approved.append(patch)

    tier_c = [i for i in issues if i.tier == "C"]
    tier_b = [i for i in issues if i.tier == "B"]
    return AuditResult(passed=not tier_c and not tier_b, issues=issues, approved_patches=approved)


def validate_new_row(row: WbsRow) -> list[AuditIssue]:
    issues: list[AuditIssue] = []
    if row.action and not row.project:
        issues.append(_tier_c("NO_PROJECT", f"行{row.sheet_row}: 工程だけの行は不可"))
    if row.state and row.state not in VALID_STATES:
        issues.append(_tier_c("INVALID_STATE", f"行{row.sheet_row}: 不正な状態 {row.state}"))
    return issues
