from __future__ import annotations

from wbs_engine.models import CellPatch, CompletionCandidate


def merge_patches(*groups: list[CellPatch]) -> list[CellPatch]:
    order = {Confidence.LOW: 0, Confidence.MED: 1, Confidence.HIGH: 2}
    merged: dict[tuple[int, str], CellPatch] = {}
    for group in groups:
        for patch in group:
            key = (patch.sheet_row, patch.column)
            if key in merged:
                prev = merged[key]
                if order[patch.confidence] >= order[prev.confidence]:
                    merged[key] = patch
            else:
                merged[key] = patch
    return list(merged.values())


def candidates_to_patches(candidates: list[CompletionCandidate]) -> list[CellPatch]:
    patches: list[CellPatch] = []
    for cand in candidates:
        patches.append(
            CellPatch(
                sheet_row=cand.sheet_row,
                column="state",
                old_value="",
                new_value=cand.new_state,
                reason=cand.reason,
                confidence=cand.confidence,
                evidence_url=cand.evidence_url,
            )
        )
        if cand.completed_at:
            patches.append(
                CellPatch(
                    sheet_row=cand.sheet_row,
                    column="completed_at",
                    old_value="",
                    new_value=cand.completed_at,
                    reason=cand.reason,
                    confidence=cand.confidence,
                )
            )
        if cand.evidence_url:
            patches.append(
                CellPatch(
                    sheet_row=cand.sheet_row,
                    column="evidence",
                    old_value="",
                    new_value=cand.evidence_url,
                    reason=cand.reason,
                    confidence=cand.confidence,
                )
            )
        if cand.reason:
            patches.append(
                CellPatch(
                    sheet_row=cand.sheet_row,
                    column="next_action",
                    old_value="",
                    new_value=cand.reason[:200],
                    reason="推察更新",
                    confidence=cand.confidence,
                )
            )
    return patches
