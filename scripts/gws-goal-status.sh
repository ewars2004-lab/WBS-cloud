#!/usr/bin/env bash
# 北極星の達成状況を一覧（docs/GWS_NORTH_STAR.md）
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
FAIL=0

echo "=== GWS 北極星ステータス ==="
echo "正本: docs/GWS_NORTH_STAR.md"
echo ""

echo "--- L1-L3 ローカル ---"
if bash scripts/gws-verify-workspace.sh; then
  :
else
  FAIL=1
fi

echo ""
echo "--- C1 Dashboard Secrets ---"
if python3 scripts/cloud-agent-ui-launch.py --secrets-only 2>/dev/null; then
  :
else
  echo "❌ C1: Secrets 不足"
  FAIL=1
fi

echo ""
echo "--- C2' Cloud 経路ドライラン（Agent 起動しない） ---"
if bash scripts/gws-dry-run-cloud-verify.sh >/tmp/gws-dry-run-cloud.log 2>&1; then
  echo "✅ C2': Secrets → cloud-install → verify 経路 OK"
else
  echo "❌ C2' NG"
  tail -20 /tmp/gws-dry-run-cloud.log
  FAIL=1
fi

echo ""
echo "--- C2 Cloud VM 本番（任意・Agent 1本だけ） ---"
echo "止めた Agent は再開しない。新規1本だけ:"
echo "  open https://cursor.com/agents"
echo "  bash scripts/cloud-install.sh && bash scripts/verify-cloud-ready.sh"

if [[ "$FAIL" -eq 0 ]]; then
  echo ""
  echo "北極星: ローカル + Secrets + Cloud 経路ドライランまで OK。"
  echo "VM 本番確認は任意（Agent 1本・手動）。"
  exit 0
fi
exit 1
