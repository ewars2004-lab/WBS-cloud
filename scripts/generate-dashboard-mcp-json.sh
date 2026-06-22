#!/usr/bin/env bash
# Dashboard → Agents → MCP に貼り付ける google-workspace-aircloset 設定を生成
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PICKLE="${HOME}/.config/gws-aircloset/python-credentials.pickle"
OUT="${REPO_ROOT}/.local/dashboard-mcp-google.json"

if [[ ! -f "$PICKLE" ]]; then
  echo "ERROR: $PICKLE がありません。Desktop で Sheets OAuth を先に完了してください。" >&2
  exit 1
fi

mkdir -p "${REPO_ROOT}/.local"
B64=$(base64 < "$PICKLE" | tr -d '\n')

python3 - "$OUT" "$B64" <<'PY'
import json, sys
out, b64 = sys.argv[1], sys.argv[2]
cfg = {
    "mcpServers": {
        "google-workspace-aircloset": {
            "command": "python3",
            "args": ["scripts/aircloset-sheets-mcp-cloud.py"],
            "env": {"GWS_CREDENTIALS_PICKLE_B64": b64},
        }
    }
}
with open(out, "w", encoding="utf-8") as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)
PY

echo "✅ 生成: $OUT"
echo ""
echo "次の操作（1回だけ）:"
echo "1. open https://cursor.com/agents"
echo "2. MCP 設定 → Add / Edit → google-workspace-aircloset"
echo "3. 上記 JSON の mcpServers.google-workspace-aircloset ブロックを貼る"
echo "   （env に認証値入り。他人に共有しない）"
echo ""
echo "または Secrets タブに Name=GWS_CREDENTIALS_PICKLE_B64 も追加可（stdio は env 直書き推奨）"
