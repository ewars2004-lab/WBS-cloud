#!/usr/bin/env python3
"""Cursor Dashboard Secrets を Google Chrome (CDP) で登録する（デュアル GWS）。"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from gws_chrome_lib import connect_page, log, wait_for_url

DASHBOARD_URL = "https://cursor.com/dashboard/cloud-agents"

SECRETS = [
    ("GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET", REPO / ".local" / "GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET.txt"),
    ("GWS_CREDENTIALS_PICKLE_B64_PERSONAL", REPO / ".local" / "GWS_CREDENTIALS_PICKLE_B64_PERSONAL.txt"),
]


def secret_exists(page, name: str) -> bool:
    try:
        return page.get_by_text(name, exact=True).count() > 0
    except Exception:
        return False


def add_secret(page, name: str, secret_value: str) -> None:
    page.goto(DASHBOARD_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(2500)

    if not wait_for_url(page, "cursor.com/dashboard", timeout_sec=120):
        log("Chrome で Cursor にログインしてください…")
        if not wait_for_url(page, "cursor.com/dashboard", timeout_sec=300):
            raise RuntimeError("Dashboard に到達できませんでした")

    if secret_exists(page, name) or name in page.inner_text("body"):
        log(f"✅ Secret '{name}' は既に登録済み")
        return

    page.get_by_role("button", name="Add Secrets").last.scroll_into_view_if_needed()
    page.get_by_role("button", name="Add Secrets").last.click()
    page.wait_for_timeout(1000)

    name_input = page.get_by_label("Name", exact=True)
    if name_input.count() == 0:
        name_input = page.locator('input[placeholder*="secret name" i]').last
    name_input.fill(name)

    value_input = page.get_by_label("Value", exact=True)
    if value_input.count() == 0:
        value_input = page.locator('input[type="password"], textarea').last
    value_input.fill(secret_value)
    page.wait_for_timeout(500)

    for i in range(page.get_by_role("button", name="Save").count()):
        btn = page.get_by_role("button", name="Save").nth(i)
        if not btn.is_disabled():
            btn.click()
            break
    page.wait_for_timeout(3000)
    page.reload(wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    if secret_exists(page, name) or name in page.inner_text("body"):
        log(f"✅ Secret '{name}' を登録しました")
    else:
        shot = REPO / ".local" / f"chrome-setup-{name}.png"
        page.screenshot(path=str(shot), full_page=True)
        log(f"⚠️ '{name}' 登録未確認 → {shot}")


def main() -> int:
    missing = [name for name, path in SECRETS if not path.is_file()]
    if missing:
        log(f"ERROR: .local に Secret ファイルがありません: {missing}")
        log("先に: bash scripts/prepare-dual-secrets.sh")
        return 1

    try:
        import playwright  # noqa: F401
    except ImportError:
        log("playwright 未インストール → pip3 install playwright && playwright install chromium")
        return 1

    pw, browser, page = connect_page(DASHBOARD_URL)
    try:
        for name, path in SECRETS:
            add_secret(page, name, path.read_text(encoding="utf-8").strip())
    finally:
        browser.close()
        pw.stop()

    log("Dashboard Secrets 完了")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
