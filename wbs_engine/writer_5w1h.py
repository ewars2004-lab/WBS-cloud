from __future__ import annotations

from datetime import datetime, timezone, timedelta

from wbs_engine.models import CellPatch, CompletionCandidate, WbsRow


def enrich_candidate_patches(candidate: CompletionCandidate, row: WbsRow) -> list[CellPatch]:
    patches: list[CellPatch] = []
    if candidate.new_state == "進行中" and not row.when:
        patches.append(
            CellPatch(
                sheet_row=row.sheet_row,
                column="when",
                old_value=row.when,
                new_value=datetime.now(timezone(timedelta(hours=9))).strftime("%Y/%m/%d"),
                reason="推察更新: 進行開始",
                confidence=candidate.confidence,
            )
        )
    if candidate.new_state == "完了" and not row.what:
        patches.append(
            CellPatch(
                sheet_row=row.sheet_row,
                column="what",
                old_value=row.what,
                new_value=f"{row.action}が完了し、次工程へ進める状態",
                reason="5W1H自動補完",
                confidence=candidate.confidence,
            )
        )
    if candidate.new_state == "完了" and not row.how and candidate.evidence_url:
        patches.append(
            CellPatch(
                sheet_row=row.sheet_row,
                column="how",
                old_value=row.how,
                new_value=f"Slack根拠リンクを開き、{row.action}の完了宣言・成果物を確認する",
                reason="5W1H自動補完",
                confidence=candidate.confidence,
            )
        )
    return patches
