#!/usr/bin/env bash
# Cloud Agent 起動直後の検証（デュアル GWS + WBS Sheets）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FAIL=0

echo "=== WBS-cloud Cloud 検証（デュアル GWS） ==="

check_secret() {
  local name="$1"
  local val="${!name:-}"
  if [[ -n "$val" ]]; then
    echo "✅ ${name}: 設定済み (len=${#val})"
  else
    echo "❌ ${name}: 未設定"
    echo "   → Dashboard → Cloud Agents → Secrets に登録後、Agent を再起動"
    FAIL=1
  fi
}

check_secret GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET
check_secret GWS_CREDENTIALS_PICKLE_B64_PERSONAL

echo ""
echo "--- cloud-install ---"
bash scripts/cloud-install.sh || FAIL=1

echo ""
echo "--- gws-verify aircloset ---"
if GWS_CONFIG_DIR="${HOME}/.config/gws-aircloset" \
   python3 scripts/gws-verify-profile.py aircloset >/tmp/wbs-verify-aircloset.json 2>/tmp/wbs-verify-aircloset.err; then
  echo "✅ aircloset GWS OK"
  head -3 /tmp/wbs-verify-aircloset.json
else
  echo "❌ aircloset GWS NG"
  cat /tmp/wbs-verify-aircloset.err
  FAIL=1
fi

echo ""
echo "--- gws-verify personal ---"
if GWS_CONFIG_DIR="${HOME}/.config/gws" \
   python3 scripts/gws-verify-profile.py personal >/tmp/wbs-verify-personal.json 2>/tmp/wbs-verify-personal.err; then
  echo "✅ personal GWS OK"
  head -3 /tmp/wbs-verify-personal.json
else
  echo "❌ personal GWS NG"
  cat /tmp/wbs-verify-personal.err
  FAIL=1
fi

echo ""
echo "--- sheets-cli verify (aircloset) ---"
if GWS_CONFIG_DIR="${HOME}/.config/gws-aircloset" \
   python3 scripts/sheets-cli.py verify >/tmp/wbs-verify-sheets.json 2>/tmp/wbs-verify-sheets.err; then
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
  echo "検証OK（GWS 両方 + Sheets）。Slack も OK なら WBS 更新開始可。"
  exit 0
fi
echo ""
echo "検証NG — 上記を修正して再実行"
exit 1
