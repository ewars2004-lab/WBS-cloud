import json
from pathlib import Path

from wbs_engine.md_calendar import md_to_wbs_patches, parse_md_grid
from wbs_engine.cartographer import parse_wbs_values
from wbs_engine.auditor import audit_patches


FIXTURE = Path(__file__).parent / "fixtures" / "md_mini.json"


def test_md_pipeline_fixture():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    deadlines = parse_md_grid(data["grid"], data["values"])
    wbs_rows = parse_wbs_values(data["wbs_values"], first_row=3927)
    patches = md_to_wbs_patches(deadlines, wbs_rows)
    rows_by_num = {r.sheet_row: r for r in wbs_rows}
    audit = audit_patches(patches, rows_by_num)
    assert len(deadlines) >= 1
    assert audit.passed or len(patches) == 0
