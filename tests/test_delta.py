from wbs_engine.delta import merge_patches
from wbs_engine.models import CellPatch, Confidence


def test_merge_patches_dedupes():
    a = CellPatch(10, "state", "", "進行中", "a", Confidence.LOW)
    b = CellPatch(10, "state", "", "完了", "b", Confidence.HIGH)
    merged = merge_patches([a], [b])
    assert len(merged) == 1
    assert merged[0].new_value == "完了"
