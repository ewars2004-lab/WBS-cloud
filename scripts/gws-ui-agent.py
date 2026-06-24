#!/usr/bin/env python3
"""UI exploration agent: screenshot + accessibility heuristics for Cursor Dashboard."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gws_chrome_lib import connect_page, log, wait_for_url

REPO = Path(__file__).resolve().parent.parent
SHOT_DIR = REPO / ".local" / "ui-agent"
VISUAL = os.environ.get("GWS_VISUAL", "0") == "1"
DEBUG_SHOTS = os.environ.get("GWS_DEBUG", "0") == "1"
API_KEY_FILE = Path.home() / ".config/cursor/cloud-api-key"
KEY_PATTERN = re.compile(r"\b(key_[A-Za-z0-9_-]{20,})\b")
INTEGRATIONS_URL = "https://cursor.com/dashboard?tab=integrations"
SECRETS_URL = "https://cursor.com/dashboard/cloud-agents"


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _score(text: str, keywords: list[str]) -> float:
    t = _norm(text)
    if not t:
        return 0.0
    best = 0.0
    for kw in keywords:
        k = _norm(kw)
        if k in t:
            best = max(best, 1.0 + len(k) / 100)
        for part in k.split():
            if part in t:
                best = max(best, 0.5)
    return best


def collect_clickables(page) -> list[dict]:
    items: list[dict] = []
    selectors = "button, a, [role='button'], [role='tab'], [role='link']"
    for i, el in enumerate(page.locator(selectors).all()):
        try:
            if not el.is_visible():
                continue
            text = (el.inner_text() or "")[:200]
            aria = el.get_attribute("aria-label") or ""
            label = text or aria
            if not label.strip():
                continue
            items.append({"index": i, "label": label.strip(), "selector": selectors})
        except Exception:
            continue
    return items


def click_best(page, keywords: list[str], min_score: float = 0.5) -> bool:
    best_score = 0.0
    best_el = None
    for el in page.locator("button, a, [role='button'], [role='tab'], [role='link']").all():
        try:
            if not el.is_visible():
                continue
            text = (el.inner_text() or "") + " " + (el.get_attribute("aria-label") or "")
            sc = _score(text, keywords)
            if sc > best_score:
                best_score = sc
                best_el = el
        except Exception:
            continue
    if best_el and best_score >= min_score:
        best_el.scroll_into_view_if_needed()
        best_el.click(timeout=8000)
        return True
    return False


def fill_last_input(page, value: str) -> bool:
    for sel in ('input[type="password"]', "textarea", 'input:not([type="hidden"])'):
        loc = page.locator(sel)
        if loc.count() == 0:
            continue
        try:
            target = loc.last
            if target.is_visible():
                target.fill(value)
                return True
        except Exception:
            continue
    return False


def fill_by_label(page, label: str, value: str) -> bool:
    for strategy in (
        lambda: page.get_by_label(label, exact=False),
        lambda: page.locator(f'input[placeholder*="{label}" i]'),
        lambda: page.get_by_placeholder(label, exact=False),
    ):
        try:
            loc = strategy()
            if loc.count() > 0 and loc.first.is_visible():
                loc.first.fill(value)
                return True
        except Exception:
            pass
    return False


def extract_api_key(page) -> str | None:
    body = page.inner_text("body")
    m = KEY_PATTERN.search(body)
    if m:
        return m.group(1)
    for loc in page.locator("code, pre, input[readonly], textarea").all():
        try:
            tag = loc.evaluate("el => el.tagName")
            text = loc.input_value() if tag in ("INPUT", "TEXTAREA") else loc.inner_text()
        except Exception:
            text = ""
        m = KEY_PATTERN.search(text or "")
        if m:
            return m.group(1)
    return None


def save_step(page, goal: str, step: int) -> Path | None:
    if not DEBUG_SHOTS:
        return None
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SHOT_DIR / f"{goal}-step{step:02d}.png"
    page.screenshot(path=str(path), full_page=True)
    return path


def narrate(msg: str) -> None:
    if VISUAL:
        log(f"👁 {msg}")
    else:
        log(msg)


def run_api_key(max_steps: int = 20) -> int:
    if API_KEY_FILE.is_file() and API_KEY_FILE.read_text(encoding="utf-8").strip():
        log(f"✅ API key 既存: {API_KEY_FILE}")
        return 0

    narrate("Chrome で Cursor Integrations を開きます（横のウィンドウを見てください）")
    pw, browser, page = connect_page(INTEGRATIONS_URL)
    stuck = 0
    try:
        for step in range(1, max_steps + 1):
            save_step(page, "api_key", step)
            key = extract_api_key(page)
            if key:
                API_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
                API_KEY_FILE.write_text(key + "\n", encoding="utf-8")
                API_KEY_FILE.chmod(0o600)
                log(f"✅ API key 保存: {API_KEY_FILE}")
                return 0

            if "authenticator" in page.url or "login" in page.url.lower():
                log("TIER3: Cursor ログイン/指紋が必要 → 完了したらチャットで「続けて」")
                return 2

            if not wait_for_url(page, "cursor.com/dashboard", timeout_sec=3):
                page.goto(INTEGRATIONS_URL, wait_until="domcontentloaded")

            progressed = False
            if step <= 3:
                narrate(f"ステップ{step}: API キー作成ボタンを探してクリック")
                progressed = click_best(
                    page,
                    ["create api key", "api key", "new api key", "generate api key", "cloud agents api"],
                )
            if not progressed:
                narrate(f"ステップ{step}: 確認ボタンを探す / スクロール")
                progressed = click_best(page, ["create", "generate", "confirm", "continue", "save"])
            if not progressed:
                page.mouse.wheel(0, 400)
                page.wait_for_timeout(500)

            page.wait_for_timeout(1500)
            if not progressed:
                stuck += 1
            else:
                stuck = 0
            if stuck >= 4:
                log("TIER3: 操作が停滞 → Chrome を確認し、必要ならログイン後「続けて」")
                return 2
        log("⚠️ API key 取得タイムアウト")
        return 1
    finally:
        browser.close()
        pw.stop()


def run_add_secret(name: str, value: str, max_steps: int = 20) -> int:
    pw, browser, page = connect_page(SECRETS_URL)
    try:
        if name in page.inner_text("body"):
            log(f"✅ Secret 既存: {name}")
            return 0
        for step in range(1, max_steps + 1):
            save_step(page, f"secret-{name}", step)
            page.goto(SECRETS_URL, wait_until="domcontentloaded")
            page.wait_for_timeout(1500)
            if name in page.inner_text("body"):
                log(f"✅ Secret 登録確認: {name}")
                return 0
            if click_best(page, ["add secrets", "add secret", "new secret"]):
                page.wait_for_timeout(800)
                fill_by_label(page, "Name", name) or fill_last_input(page, name)
                fill_by_label(page, "Value", value)
                click_best(page, ["save", "add", "confirm"])
                page.wait_for_timeout(2000)
                continue
            page.mouse.wheel(0, 400)
        return 1
    finally:
        browser.close()
        pw.stop()


def main() -> int:
    parser = argparse.ArgumentParser(description="GWS UI exploration agent")
    parser.add_argument("goal", choices=["api_key", "secret", "snapshot"])
    parser.add_argument("--name", help="Secret name for goal=secret")
    parser.add_argument("--value-file", help="Secret value file for goal=secret")
    parser.add_argument("--url", default=INTEGRATIONS_URL)
    parser.add_argument("--max-steps", type=int, default=20)
    args = parser.parse_args()

    try:
        import playwright  # noqa: F401
    except ImportError:
        log("pip3 install playwright")
        return 1

    if args.goal == "api_key":
        return run_api_key(args.max_steps)
    if args.goal == "secret":
        if not args.name or not args.value_file:
            log("secret には --name と --value-file が必要")
            return 1
        val = Path(args.value_file).read_text(encoding="utf-8").strip()
        return run_add_secret(args.name, val, args.max_steps)
    if args.goal == "snapshot":
        pw, browser, page = connect_page(args.url)
        try:
            p = save_step(page, "snapshot", 1)
            log(f"saved: {p}")
            return 0
        finally:
            browser.close()
            pw.stop()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
