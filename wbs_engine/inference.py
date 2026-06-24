from __future__ import annotations

import re
from datetime import datetime

from wbs_engine.config import load_json
from wbs_engine.models import Confidence, CompletionCandidate, SlackEvent


HIGH_PATTERNS = [
    r"修正しました",
    r"対応完了",
    r"確認OK",
    r"結合テスト完了",
    r"SYSTEM TEST完了",
    r"総合テスト完了",
    r"リリースしました",
    r"本番確認済み",
    r"依頼はないです",
    r"転記しました",
    r"クローズ",
]

MED_PATTERNS = [
    r"Figma",
    r"総合テスト",
    r"STG",
    r"PROD",
    r"アサイン",
    r"インプット",
    r"見積もり",
    r"FIX",
    r"デプロイ",
]

LOW_PATTERNS = [
    r"確認します",
    r"対応します",
    r"いけそう",
    r"あとで見る",
    r"たぶん",
    r"検討します",
]

STANDARD_PHASES = [
    "5W1H",
    "5W1H修正",
    "Figma作成",
    "Figma修正",
    "機能一覧作成",
    "機能一覧修正",
    "総合テスト作成",
    "総合テスト修正",
    "エンジニア見積もりMTG",
    "インプットMTG",
    "開発進捗管理",
    "総合テストの実施",
    "リリース",
    "リリース後テスト",
]


def classify_text(text: str) -> Confidence:
    for pat in LOW_PATTERNS:
        if re.search(pat, text, re.I):
            return Confidence.LOW
    for pat in HIGH_PATTERNS:
        if re.search(pat, text, re.I):
            return Confidence.HIGH
    for pat in MED_PATTERNS:
        if re.search(pat, text, re.I):
            return Confidence.MED
    return Confidence.LOW


def infer_phase_from_text(text: str, action: str = "") -> str | None:
    if action:
        for phase in STANDARD_PHASES:
            if phase in action:
                return phase
    for phase in STANDARD_PHASES:
        if phase in text:
            return phase
    if re.search(r"総合テスト", text, re.I):
        return "総合テスト作成"
    if re.search(r"Figma", text, re.I):
        return "Figma作成"
    if re.search(r"FB|フィードバック", text, re.I):
        return "FB"
    if re.search(r"計画作成|MD", text, re.I):
        return "計画作成"
    return None


def slack_ts_to_jst(ts: str) -> str:
    try:
        sec = float(ts.split(".")[0])
        return datetime.fromtimestamp(sec).strftime("%Y/%m/%d %H:%M JST")
    except (ValueError, OSError):
        return ""


def events_to_candidates(
    events: list[SlackEvent],
    rows_by_project: dict[str, list],
) -> list[CompletionCandidate]:
    candidates: list[CompletionCandidate] = []
    for event in events:
        confidence = classify_text(event.text)
        if confidence == Confidence.LOW:
            continue
        for key in event.project_keys:
            project_rows = []
            for proj, proj_rows in rows_by_project.items():
                if key.replace("pj_", "") in proj or key in proj:
                    project_rows = proj_rows
                    break
            if not project_rows:
                continue
            phase = infer_phase_from_text(event.text)
            target = None
            for row in project_rows:
                if phase and phase in row.action:
                    target = row
                    break
            if not target:
                target = next((r for r in project_rows if r.state != "完了"), None)
            if not target:
                continue
            if confidence == Confidence.MED and target.state == "完了":
                continue
            new_state = "完了" if confidence == Confidence.HIGH else "進行中"
            if confidence == Confidence.MED and new_state == "完了":
                new_state = "進行中"
            candidates.append(
                CompletionCandidate(
                    sheet_row=target.sheet_row,
                    project=target.project,
                    action=target.action,
                    new_state=new_state,
                    completed_at=slack_ts_to_jst(event.message_ts) if new_state == "完了" else "",
                    evidence_url=event.permalink,
                    reason=f"Slack signal ({confidence.value}): {event.text[:120]}",
                    confidence=confidence,
                )
            )
    return candidates
