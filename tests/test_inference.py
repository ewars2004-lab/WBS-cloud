from wbs_engine.inference import classify_text, infer_phase_from_text
from wbs_engine.models import Confidence


def test_high_confidence():
    assert classify_text("修正しました！依頼はないです") == Confidence.HIGH


def test_low_confidence():
    assert classify_text("確認します、いけそうです") == Confidence.LOW


def test_infer_phase():
    assert infer_phase_from_text("総合テストリンク共有") == "総合テスト作成"
