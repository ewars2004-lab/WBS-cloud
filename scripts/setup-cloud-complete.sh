#!/usr/bin/env bash
# ローカル Mac で1回実行: Cloud Agent 完遂に必要な認証・MCP 設定を準備
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== WBS-cloud Cloud Agent セットアップ ==="
echo ""

# 1. Dashboard MCP JSON（認証入り・gitignore）
"${REPO_ROOT}/scripts/generate-dashboard-mcp-json.sh"

MCP_BLOCK="${REPO_ROOT}/.local/dashboard-mcp-google-block.json"
python3 - "$REPO_ROOT/.local/dashboard-mcp-google.json" "$MCP_BLOCK" <<'PY'
import json, sys
src, dst = sys.argv[1], sys.argv[2]
with open(src, encoding="utf-8") as f:
    block = json.load(f)["mcpServers"]["google-workspace-aircloset"]
with open(dst, "w", encoding="utf-8") as f:
    json.dump(block, f, indent=2, ensure_ascii=False)
PY

# 2. Secrets 用 base64（MCP 未登録でも CLI フォールバック可）
SECRET_FILE="${REPO_ROOT}/.local/GWS_CREDENTIALS_PICKLE_B64.txt"
mkdir -p "${REPO_ROOT}/.local"
base64 < "${HOME}/.config/gws-aircloset/python-credentials.pickle" | tr -d '\n' > "$SECRET_FILE"
echo ""
echo "--- Cloud Agents → Secrets（最低限これで CLI フォールバック可）---"
echo "Name:  GWS_CREDENTIALS_PICKLE_B64"
echo "Value: ${SECRET_FILE} の内容をコピー"
if command -v pbcopy >/dev/null 2>&1; then
  pbcopy < "$SECRET_FILE"
  echo "（Secret 値をクリップボードにコピー済み → Dashboard Secrets に貼る）"
fi

# 3. MCP ブロックもクリップボード用に別ファイル
echo ""
echo "--- Agents → MCP → google-workspace-aircloset（MCP ツールを使う場合）---"
echo "貼り付け用: ${MCP_BLOCK}"
echo "（MCP 登録時: pbcopy < .local/dashboard-mcp-google-block.json）"

echo ""
echo "手順（約2分）:"
echo "  A. https://cursor.com/dashboard/cloud-agents → Secrets"
echo "     → Add: GWS_CREDENTIALS_PICKLE_B64（クリップボードの値を貼る）"
echo "  B. （任意）https://cursor.com/agents → MCP → google-workspace-aircloset"
echo "     → pbcopy < .local/dashboard-mcp-google-block.json でコピーして貼る"
echo "  C. Slack MCP が Connect 済みか確認"
echo "  D. Cloud Agent で ewars2004-lab/WBS-cloud を選び検証プロンプト実行"
echo ""
echo "検証プロンプトは docs/CLOUD_SETUP.md の「初回検証プロンプト」を参照"
echo ""

if command -v open >/dev/null 2>&1; then
  open "https://cursor.com/dashboard/cloud-agents"
  sleep 1
  open "https://cursor.com/agents"
fi
