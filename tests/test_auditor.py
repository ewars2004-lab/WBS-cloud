from wbs_engine.auditor import audit_patches
from wbs_engine.models import CellPatch, Confidence, RowKind, WbsRow


def test_f_column_forbidden_for_aircloset():
    row = WbsRow(sheet_row=10, kind=RowKind.TASK, project="AIRCLOSET-100031 x", action="5W1H")
    patches = [CellPatch(sheet_row=10, column="due", old_value="", new_value="2026/06/30", reason="x", confidence=Confidence.HIGH)]
    result = audit_patches(patches, {10: row})
    assert not result.passed
    assert any(i.code == "F_FORBIDDEN" for i in result.issues)


def test_f_column_allowed_for_md_brand():
    row = WbsRow(sheet_row=20, kind=RowKind.MD_BRAND, project="NOLLEYS：WI", action="計画作成")
    patches = [CellPatch(sheet_row=20, column="due", old_value="", new_value="2026/06/30", reason="md", confidence=Confidence.HIGH)]
    result = audit_patches(patches, {20: row})
    assert result.passed
    assert len(result.approved_patches) == 1


def test_completion_needs_evidence():
    row = WbsRow(sheet_row=10, kind=RowKind.TASK, project="AIRCLOSET-100031", action="5W1H")
    patches = [
        CellPatch(sheet_row=10, column="state", old_value="進行中", new_value="完了", reason="done", confidence=Confidence.MED),
    ]
    result = audit_patches(patches, {10: row})
    assert not result.passed
    assert any(i.code == "MISSING_EVIDENCE" for i in result.issues)
