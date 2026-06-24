#!/usr/bin/env bash
# ローカル Mac で1回実行: Cloud Agent 完遂に必要な認証・MCP 設定を準備（デュアル GWS）
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== WBS-cloud Cloud Agent セットアップ（デュアル GWS） ==="
echo ""

# 1. Dashboard MCP JSON（Secrets 連携版・Cloud VM パス）
"${REPO_ROOT}/scripts/generate-dashboard-mcp-json.sh" --cloud

# 2. 両プロファイルの Secrets 用 base64
bash "${REPO_ROOT}/scripts/prepare-dual-secrets.sh"

echo ""
echo "--- Cloud Agents → Secrets（2つ登録）---"
echo "  GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET  ← .local/GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET.txt"
echo "  GWS_CREDENTIALS_PICKLE_B64_PERSONAL   ← .local/GWS_CREDENTIALS_PICKLE_B64_PERSONAL.txt"

if command -v pbcopy >/dev/null 2>&1 && [[ -f "${REPO_ROOT}/.local/GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET.txt" ]]; then
  pbcopy < "${REPO_ROOT}/.local/GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET.txt"
  echo "（aircloset Secret をクリップボードにコピー済み）"
fi

echo ""
echo "手順（約3分）:"
echo "  A. https://cursor.com/dashboard/cloud-agents → Secrets"
echo "     → 上記2つを登録（済ならスキップ）"
echo "  B. https://cursor.com/dashboard/integrations → MCP"
echo "     → .local/dashboard-mcp-dual.json の mcpServers を貼る"
echo "  C. Slack MCP が Connect 済みか確認"
echo "  D. Cloud Agent で ewars2004-lab/WBS-cloud を選び bash scripts/verify-cloud-ready.sh"
echo ""
echo "MCP env に認証を直書きする場合:"
echo "  bash scripts/generate-dashboard-mcp-json.sh --embed-b64"
echo ""
echo "User Rule（Cursor Settings → Rules）:"
echo "  docs/CURSOR_USER_RULE_GWS.md の内容を貼る"
echo ""
echo "=== 完全自動起動（API キーがある場合）==="
echo "  ./scripts/launch-wbs-cloud-agent.sh launch"

if command -v open >/dev/null 2>&1; then
  open "https://cursor.com/dashboard/cloud-agents"
  sleep 1
  open "https://cursor.com/dashboard/integrations"
fi
