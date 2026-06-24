from wbs_engine.md_calendar import match_color_key, normalize_brand, wbs_key_for_md


def test_normalize_brand():
    assert normalize_brand("NOLLEY'S") == "NOLLEYS"


def test_wbs_key():
    assert wbs_key_for_md("NOLLEYS", "WI") == "NOLLEYS：WI"


def test_match_pink():
    key = match_color_key((0.957, 0.8, 0.8), {
        "md_pink_namy": {"rgb": [0.957, 0.8, 0.8], "tolerance": 0.06, "role": "md_deadline"}
    })
    assert key == "md_pink_namy"
