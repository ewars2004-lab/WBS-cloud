from __future__ import annotations

import json
import os
import re
from pathlib import Path

from wbs_engine.cartographer import extract_project_keys
from wbs_engine.config import REPO_ROOT, STATE_DIR, load_json
from wbs_engine.models import SlackEvent


def parse_slack_export_item(item: dict) -> SlackEvent | None:
    text = str(item.get("text", "") or "")
    if not text.strip():
        return None
    channel_id = str(item.get("channel_id", "") or item.get("channel", ""))
    channel_name = str(item.get("channel_name", "") or item.get("channel", ""))
    ts = str(item.get("message_ts", "") or item.get("ts", ""))
    permalink = str(item.get("permalink", "") or item.get("url", ""))
    user = str(item.get("user", "") or item.get("from", ""))
    thread_ts = str(item.get("thread_ts", "") or "")
    keys = extract_project_keys(text)
    keys.extend(extract_project_keys(channel_name))
    if not keys and not permalink:
        return None
    return SlackEvent(
        channel_id=channel_id,
        channel_name=channel_name,
        message_ts=ts,
        permalink=permalink,
        text=text,
        user=user,
        thread_ts=thread_ts,
        project_keys=list(dict.fromkeys(keys)),
    )


def load_events_from_json(path: Path) -> list[SlackEvent]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    items = raw if isinstance(raw, list) else raw.get("events", raw.get("messages", []))
    events: list[SlackEvent] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        ev = parse_slack_export_item(item)
        if ev:
            events.append(ev)
    return events


def load_inbox_events() -> list[SlackEvent]:
    inbox = STATE_DIR / "inbox"
    if not inbox.exists():
        return []
    events: list[SlackEvent] = []
    for path in sorted(inbox.glob("*.json")):
        events.extend(load_events_from_json(path))
    return events


def fetch_slack_api_events(channel_names: list[str] | None = None) -> list[SlackEvent]:
    token = os.environ.get("SLACK_BOT_TOKEN", "").strip()
    if not token:
        return []
    try:
        import urllib.error
        import urllib.request

        patterns = load_json("channel_patterns.json")
        channels = channel_names or patterns.get("scout_channels", [])
        events: list[SlackEvent] = []
        for ch in channels:
            q = ch if ch.startswith("#") else f"#{ch}"
            url = f"https://slack.com/api/search.messages?query=in:{q}&count=20"
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
            if not data.get("ok"):
                continue
            for match in data.get("messages", {}).get("matches", []):
                text = match.get("text", "")
                keys = extract_project_keys(text)
                events.append(
                    SlackEvent(
                        channel_id=match.get("channel", {}).get("id", ""),
                        channel_name=match.get("channel", {}).get("name", ch),
                        message_ts=match.get("ts", ""),
                        permalink=match.get("permalink", ""),
                        text=text,
                        user=match.get("username", ""),
                        project_keys=keys,
                    )
                )
        return events
    except Exception:
        return []


def collect_slack_events() -> list[SlackEvent]:
    events = load_inbox_events()
    if events:
        return events
    return fetch_slack_api_events()


def save_inbox_events(events: list[SlackEvent], filename: str = "slack_events.json") -> Path:
    inbox = STATE_DIR / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    path = inbox / filename
    payload = [
        {
            "channel_id": e.channel_id,
            "channel_name": e.channel_name,
            "message_ts": e.message_ts,
            "permalink": e.permalink,
            "text": e.text,
            "user": e.user,
            "thread_ts": e.thread_ts,
        }
        for e in events
    ]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
