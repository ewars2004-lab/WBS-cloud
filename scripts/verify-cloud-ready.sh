#!/usr/bin/env bash
# Cloud Agent 起動直後の検証（AGENTS.md と同内容）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FAIL=0

echo "=== WBS-cloud Cloud 検証 ==="

if [[ -n "${GWS_CREDENTIALS_PICKLE_B64:-}" ]]; then
  echo "✅ GWS_CREDENTIALS_PICKLE_B64: 設定済み (len=${#GWS_CREDENTIALS_PICKLE_B64})"
else
  echo "❌ GWS_CREDENTIALS_PICKLE_B64: 未設定"
  echo "   → Dashboard → Cloud Agents → My Secrets に登録後、Agent を再起動"
  FAIL=1
fi

echo ""
echo "--- cloud-install ---"
bash scripts/cloud-install.sh || FAIL=1

echo ""
echo "--- sheets-cli verify ---"
if python3 scripts/sheets-cli.py verify >/tmp/wbs-verify-sheets.json 2>/tmp/wbs-verify-sheets.err; then
  echo "✅ sheets-cli verify OK"
  head -3 /tmp/wbs-verify-sheets.json
else
  echo "❌ sheets-cli verify NG"
  cat /tmp/wbs-verify-sheets.err
  FAIL=1
fi

echo ""
echo "--- Slack (MCP または手動) ---"
echo "Slack 検索は MCP ツール slack_search_public_and_private で 81205 after:2026-06-19 を実行"

if [[ "$FAIL" -eq 0 ]]; then
  echo ""
  echo "検証OK（Sheets 側）。Slack も OK なら WBS 更新開始可。"
  exit 0
fi
echo ""
echo "検証NG — 上記を修正して再実行"
exit 1
