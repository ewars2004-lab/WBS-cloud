from wbs_engine.cartographer import (
    classify_row,
    extract_project_keys,
    parse_wbs_values,
)
from wbs_engine.models import RowKind


def test_classify_project_header():
    assert classify_row("AIRCLOSET-100031 foo", "") == RowKind.PROJECT_HEADER


def test_classify_md_brand():
    assert classify_row("NOLLEYS：WI", "計画作成") == RowKind.MD_BRAND


def test_parse_wbs_values():
    values = [
        ["AIRCLOSET-100031 title"],
        ["AIRCLOSET-100031 title", "5W1H", "1.0", "memo", "進行中"],
    ]
    rows = parse_wbs_values(values, first_row=6)
    assert len(rows) == 2
    assert rows[1].action == "5W1H"
    assert rows[1].state == "進行中"


def test_extract_project_keys():
    keys = extract_project_keys("pj_120303 と AIRCLOSET-100031")
    assert "AIRCLOSET-100031" in keys
    assert "pj_120303" in keys
