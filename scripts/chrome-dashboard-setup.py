#!/usr/bin/env python3
"""Cursor Dashboard Secrets を Google Chrome (CDP) で登録する。"""
from __future__ import annotations

import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SECRET_FILE = REPO / ".local" / "GWS_CREDENTIALS_PICKLE_B64.txt"
SECRET_NAME = "GWS_CREDENTIALS_PICKLE_B64"
DASHBOARD_URL = "https://cursor.com/dashboard/cloud-agents"
CDP_URL = "http://127.0.0.1:9222"
CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SRC_PROFILE = Path.home() / "Library/Application Support/Google/Chrome"
AUTOMATION_PROFILE = Path.home() / ".cursor/wbs-chrome-profile"


def log(msg: str) -> None:
    print(msg, flush=True)


def cdp_alive() -> bool:
    try:
        with urllib.request.urlopen(f"{CDP_URL}/json/version", timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def sync_chrome_profile() -> None:
    marker = AUTOMATION_PROFILE / ".synced-from-default"
    if marker.exists():
        return
    log("Chrome ログイン状態をコピーしています（初回のみ）…")
    AUTOMATION_PROFILE.mkdir(parents=True, exist_ok=True)
    src_default = SRC_PROFILE / "Default"
    dst_default = AUTOMATION_PROFILE / "Default"
    if src_default.is_dir():
        if dst_default.exists():
            shutil.rmtree(dst_default)
        shutil.copytree(src_default, dst_default, ignore=shutil.ignore_patterns("SingletonLock", "SingletonSocket", "SingletonCookie"))
    local_state = SRC_PROFILE / "Local State"
    if local_state.is_file():
        shutil.copy2(local_state, AUTOMATION_PROFILE / "Local State")
    marker.write_text("ok\n", encoding="utf-8")


def ensure_chrome_cdp() -> None:
    if cdp_alive():
        log("✅ Chrome CDP 接続済み")
        return

    subprocess.run(["pkill", "-x", "Google Chrome"], check=False)
    time.sleep(2)
    sync_chrome_profile()

    log("Google Chrome を起動しています…")
    subprocess.Popen(
        [
            CHROME_BIN,
            "--remote-debugging-port=9222",
            f"--user-data-dir={AUTOMATION_PROFILE}",
            "--no-first-run",
            "--no-default-browser-check",
            DASHBOARD_URL,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    for _ in range(40):
        if cdp_alive():
            log("✅ Chrome 起動完了")
            return
        time.sleep(1)
    raise RuntimeError("Chrome CDP 起動に失敗しました")


def wait_for_dashboard(page, timeout_sec: int = 300) -> bool:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        url = page.url
        if "cursor.com/dashboard" in url and "authenticator" not in url:
            return True
        time.sleep(1)
    return False


def click_first(page, labels: list[str], timeout_ms: int = 5000) -> bool:
    for label in labels:
        for role in ("button", "link", "tab"):
            loc = page.get_by_role(role, name=label, exact=False)
            try:
                if loc.count() > 0:
                    loc.first.click(timeout=timeout_ms)
                    return True
            except Exception:
                pass
        loc = page.get_by_text(label, exact=False)
        try:
            if loc.count() > 0:
                loc.first.click(timeout=timeout_ms)
                return True
        except Exception:
            pass
    return False


def secret_exists(page) -> bool:
    try:
        return page.get_by_text(SECRET_NAME, exact=True).count() > 0
    except Exception:
        return False


def add_secret(page, secret_value: str) -> None:
    page.goto(DASHBOARD_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(2500)

    if not wait_for_dashboard(page, timeout_sec=120):
        log("Chrome で Cursor にログインしてください（GitHub で続行）…")
        if not wait_for_dashboard(page, timeout_sec=300):
            raise RuntimeError("Dashboard に到達できませんでした")

    if secret_exists(page):
        log(f"✅ Secret '{SECRET_NAME}' は既に登録済み")
        return

    if secret_exists(page):
        log(f"✅ Secret '{SECRET_NAME}' は既に登録済み")
        return

    page.get_by_role("button", name="Add Secrets").last.scroll_into_view_if_needed()
    page.get_by_role("button", name="Add Secrets").last.click()
    page.wait_for_timeout(1000)

    name_input = page.get_by_label("Name", exact=True)
    if name_input.count() == 0:
        name_input = page.locator('input[placeholder*="secret name" i]').last
    name_input.fill(SECRET_NAME)

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
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    if secret_exists(page) or SECRET_NAME in page.inner_text("body"):
        log(f"✅ Secret '{SECRET_NAME}' を登録しました")
    else:
        page.screenshot(path=str(REPO / ".local" / "chrome-setup-after.png"), full_page=True)
        log("⚠️ 登録確認できませんでした。.local/chrome-setup-after.png を確認")


def main() -> int:
    if not SECRET_FILE.is_file():
        log(f"ERROR: {SECRET_FILE} がありません。./scripts/setup-cloud-complete.sh を実行")
        return 1

    secret_value = SECRET_FILE.read_text(encoding="utf-8").strip()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log("ERROR: pip3 install playwright")
        return 1

    ensure_chrome_cdp()

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.pages[0] if context.pages else context.new_page()
        if "cursor.com" not in page.url:
            page.goto(DASHBOARD_URL, wait_until="domcontentloaded")

        log("Dashboard に到達。Secret を登録します…")
        try:
            add_secret(page, secret_value)
        except Exception as exc:
            log(f"ERROR: {exc}")
            return 1

    log("完了（Chrome は開いたままです）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
