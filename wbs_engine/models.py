from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Confidence(str, Enum):
    HIGH = "HIGH"
    MED = "MED"
    LOW = "LOW"


class RowKind(str, Enum):
    PROJECT_HEADER = "project_header"
    TASK = "task"
    MD_HEADER = "md_header"
    MD_BRAND = "md_brand"
    OTHER = "other"


@dataclass
class WbsRow:
    sheet_row: int
    kind: RowKind
    project: str = ""
    action: str = ""
    estimate: str = ""
    next_action: str = ""
    state: str = ""
    due: str = ""
    completed_at: str = ""
    evidence: str = ""
    memo: str = ""
    when: str = ""
    where: str = ""
    who: str = ""
    what: str = ""
    why: str = ""
    how: str = ""

    @property
    def is_md_brand_row(self) -> bool:
        if self.kind == RowKind.MD_BRAND:
            return True
        if "：" in self.project and self.action:
            return True
        if self.action == "MDを期日入れる":
            return True
        return False

    @property
    def allows_f_edit(self) -> bool:
        if self.action == "MDを期日入れる":
            return True
        if self.is_md_brand_row:
            return True
        if self.project.startswith("MD関連"):
            return False
        return False


@dataclass
class CellPatch:
    sheet_row: int
    column: str
    old_value: str
    new_value: str
    reason: str
    confidence: Confidence = Confidence.HIGH
    source: str = ""
    evidence_url: str = ""


@dataclass
class SlackEvent:
    channel_id: str
    channel_name: str
    message_ts: str
    permalink: str
    text: str
    user: str = ""
    thread_ts: str = ""
    project_keys: list[str] = field(default_factory=list)


@dataclass
class CompletionCandidate:
    sheet_row: int
    project: str
    action: str
    new_state: str
    completed_at: str
    evidence_url: str
    reason: str
    confidence: Confidence
    patches: list[CellPatch] = field(default_factory=list)


@dataclass
class AuditIssue:
    tier: str
    code: str
    message: str
    patch: CellPatch | None = None


@dataclass
class AuditResult:
    passed: bool
    issues: list[AuditIssue] = field(default_factory=list)
    approved_patches: list[CellPatch] = field(default_factory=list)


@dataclass
class MdDeadline:
    year: str
    season: str
    brand: str
    buyer: str
    stage: str
    date: str
    md_row: int
    md_col: int
    color_key: str
    rgb: tuple[float, float, float]


@dataclass
class RunReport:
    run_id: str
    updated_rows: list[int] = field(default_factory=list)
    added_rows: list[int] = field(default_factory=list)
    skipped: list[dict[str, Any]] = field(default_factory=list)
    md_sync_count: int = 0
    audit_issues: list[AuditIssue] = field(default_factory=list)
