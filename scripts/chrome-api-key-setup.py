#!/usr/bin/env python3
"""Cursor Cloud Agents API キーを Chrome CDP で作成し ~/.config/cursor/cloud-api-key に保存。"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gws_chrome_lib import click_first, connect_page, log, wait_for_url

INTEGRATIONS_URL = "https://cursor.com/dashboard?tab=integrations"
API_KEY_FILE = Path.home() / ".config/cursor/cloud-api-key"
KEY_PATTERN = re.compile(r"\b(key_[A-Za-z0-9_-]{20,})\b")


def extract_key_from_page(page) -> str | None:
    body = page.inner_text("body")
    m = KEY_PATTERN.search(body)
    if m:
        return m.group(1)
    for loc in page.locator("code, pre, input[readonly], textarea").all():
        try:
            text = loc.input_value() if loc.evaluate("el => el.tagName") in ("INPUT", "TEXTAREA") else loc.inner_text()
        except Exception:
            text = loc.inner_text()
        m = KEY_PATTERN.search(text or "")
        if m:
            return m.group(1)
    return None


def main() -> int:
    if API_KEY_FILE.is_file() and API_KEY_FILE.read_text(encoding="utf-8").strip():
        log(f"✅ API key 既存: {API_KEY_FILE}")
        return 0

    try:
        import playwright  # noqa: F401
    except ImportError:
        log("pip3 install playwright && playwright install chromium")
        return 1

    API_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    pw, browser, page = connect_page(INTEGRATIONS_URL)
    try:
        if not wait_for_url(page, "cursor.com/dashboard", timeout_sec=120):
            log("Chrome で Cursor ログインが必要です（最大5分待機）…")
            if not wait_for_url(page, "cursor.com/dashboard", timeout_sec=300):
                raise RuntimeError("Dashboard に到達できませんでした")

        page.goto(INTEGRATIONS_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        click_first(
            page,
            [
                "Create API Key",
                "Create API key",
                "New API Key",
                "Generate API Key",
                "Cloud Agents API",
            ],
        )
        page.wait_for_timeout(2000)
        click_first(page, ["Create", "Generate", "Confirm", "Continue"])
        page.wait_for_timeout(3000)

        key = extract_key_from_page(page)
        if not key:
            shot = Path.home() / ".cursor/wbs-api-key-setup.png"
            page.screenshot(path=str(shot), full_page=True)
            log(f"⚠️ API key を自動取得できませんでした。手動で作成し保存:")
            log(f"  pbpaste > {API_KEY_FILE}")
            log(f"  スクリーンショット: {shot}")
            return 1

        API_KEY_FILE.write_text(key + "\n", encoding="utf-8")
        API_KEY_FILE.chmod(0o600)
        log(f"✅ API key 保存: {API_KEY_FILE}")
        return 0
    finally:
        browser.close()
        pw.stop()


if __name__ == "__main__":
    raise SystemExit(main())
