"""Shared Chrome CDP helpers for Cursor Dashboard automation."""
from __future__ import annotations

import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

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
        shutil.copytree(
            src_default,
            dst_default,
            ignore=shutil.ignore_patterns("SingletonLock", "SingletonSocket", "SingletonCookie"),
        )
    local_state = SRC_PROFILE / "Local State"
    if local_state.is_file():
        shutil.copy2(local_state, AUTOMATION_PROFILE / "Local State")
    marker.write_text("ok\n", encoding="utf-8")


def ensure_chrome_cdp(start_url: str) -> None:
    if cdp_alive():
        log("✅ Chrome CDP 接続済み")
        return

    sync_chrome_profile()

    log("Google Chrome を起動しています…")
    subprocess.Popen(
        [
            CHROME_BIN,
            "--remote-debugging-port=9222",
            f"--user-data-dir={AUTOMATION_PROFILE}",
            "--no-first-run",
            "--no-default-browser-check",
            start_url,
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


def wait_for_url(page, needle: str, timeout_sec: int = 300) -> bool:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        if needle in page.url and "authenticator" not in page.url:
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


def connect_page(start_url: str):
    from playwright.sync_api import sync_playwright

    ensure_chrome_cdp(start_url)
    pw = sync_playwright().start()
    browser = pw.chromium.connect_over_cdp(CDP_URL)
    context = browser.contexts[0] if browser.contexts else browser.new_context()
    page = context.pages[0] if context.pages else context.new_page()
    if start_url.split("/")[2] not in page.url:
        page.goto(start_url, wait_until="domcontentloaded")
    return pw, browser, page
