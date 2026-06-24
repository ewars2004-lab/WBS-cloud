#!/usr/bin/env python3
"""Cloud Agent を cursor.com/agents UI から起動（API キー不要）。"""
from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gws_chrome_lib import click_first, connect_page, log, vlog

DEFAULT_PROMPT = """AGENTS.md を読み、次を実行して結果を報告してください:

bash scripts/cloud-install.sh
bash scripts/verify-cloud-ready.sh
"""


def launch(page, repo_slug: str, prompt: str) -> str | None:
    short = repo_slug.split("/")[-1] if "/" in repo_slug else repo_slug
    page.goto("https://cursor.com/agents", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    if "authenticator" in page.url or "login" in page.url.lower():
        log("TIER3: Cursor ログインが必要 → 完了後「続けて」")
        return None

    vlog("新人エージェント → リポジトリ選択 → プロンプト入力")
    click_first(page, ["New Agent", "新人エージェント"])
    page.wait_for_timeout(2000)
    click_first(page, ["Select repository", "リポジトリを選択", "Repository"])
    page.wait_for_timeout(1000)

    for sel in ('input[placeholder*="repo" i]', 'input[type="search"]', "input"):
        loc = page.locator(sel)
        if loc.count() and loc.first.is_visible():
            loc.first.fill(short)
            break
    page.wait_for_timeout(1500)
    click_first(page, [repo_slug, short, f"ewars2004-lab/{short}"])
    page.wait_for_timeout(1000)

    ce = page.locator('[contenteditable="true"]').first
    ce.click()
    page.keyboard.press("Meta+A")
    page.keyboard.insert_text(prompt)
    page.wait_for_timeout(500)

    vlog("Start をクリック")
    for name in ("Start", "Run", "Create", "起動"):
        btn = page.get_by_role("button", name=name, exact=False)
        if btn.count():
            btn.first.click(timeout=10000)
            break
    else:
        page.keyboard.press("Enter")

    for _ in range(30):
        page.wait_for_timeout(1000)
        m = re.search(r"/agents/(bc-[a-f0-9-]+)", page.url)
        if m:
            return m.group(1)
    return None


def check_dashboard_secrets(page) -> bool:
    page.goto("https://cursor.com/dashboard/cloud-agents", wait_until="domcontentloaded")
    page.wait_for_timeout(2500)
    body = page.inner_text("body")
    ok = all(
        name in body
        for name in ("GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET", "GWS_CREDENTIALS_PICKLE_B64_PERSONAL")
    )
    if ok:
        log("✅ C1: Dashboard Secrets 両方あり")
    else:
        log("❌ C1: Dashboard Secrets 不足 → chrome-dashboard-setup.py")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="ewars2004-lab/WBS-cloud")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--secrets-only", action="store_true")
    args = parser.parse_args()

    pw, browser, page = connect_page("https://cursor.com/dashboard/cloud-agents")
    try:
        if not check_dashboard_secrets(page):
            return 2
        if args.secrets_only:
            return 0
        agent_id = launch(page, args.repo, args.prompt)
        if not agent_id:
            log("⚠️ Agent URL 未取得（起動リクエストは送信済みの可能性）")
            log("   https://cursor.com/agents で「now」の Agent を確認")
            return 0
        url = f"https://cursor.com/agents/{agent_id}"
        log(f"✅ Agent 起動: {url}")
        out = Path(__file__).resolve().parent.parent / ".local/heal/last-ui-agent.txt"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(agent_id + "\n", encoding="utf-8")
        return 0
    finally:
        browser.close()
        pw.stop()


if __name__ == "__main__":
    raise SystemExit(main())
