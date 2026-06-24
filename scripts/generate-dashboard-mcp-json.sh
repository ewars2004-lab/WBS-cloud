#!/usr/bin/env bash
# Dashboard → Cloud Agents → MCP Integrations に貼るデュアル GWS 設定を生成
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${REPO_ROOT}/.local/dashboard-mcp-dual.json"
EMBED=0
CONFIG_HOME="${HOME}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --embed-b64) EMBED=1; shift ;;
    --cloud) CONFIG_HOME="/home/ubuntu"; shift ;;
    *) echo "Usage: $0 [--embed-b64] [--cloud]" >&2; exit 1 ;;
  esac
done

mkdir -p "${REPO_ROOT}/.local"

python3 - "$OUT" "$EMBED" "$CONFIG_HOME" "$HOME" <<'PY'
import base64
import json
import sys
from pathlib import Path

out = Path(sys.argv[1])
embed = sys.argv[2] == "1"
config_home = Path(sys.argv[3])
pickle_home = Path(sys.argv[4])

profiles = [
    ("google-workspace-aircloset", config_home / ".config/gws-aircloset", pickle_home / ".config/gws-aircloset", "GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET"),
    ("google-workspace-personal", config_home / ".config/gws", pickle_home / ".config/gws", "GWS_CREDENTIALS_PICKLE_B64_PERSONAL"),
]

servers = {}
for name, config_dir, pickle_dir, secret_env in profiles:
    env = {"GWS_CONFIG_DIR": str(config_dir)}
    if embed:
        pickle_path = pickle_dir / "python-credentials.pickle"
        if not pickle_path.is_file():
            print(f"ERROR: missing {pickle_path} (run gws-oauth-login.sh first)", file=sys.stderr)
            sys.exit(1)
        env[secret_env] = base64.b64encode(pickle_path.read_bytes()).decode("ascii")
    servers[name] = {
        "command": "python3",
        "args": ["scripts/gws-python-mcp.py"],
        "env": env,
    }

cfg = {"mcpServers": servers}
out.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
PY

echo "✅ 生成: $OUT (GWS_CONFIG_DIR base: ${CONFIG_HOME})"
echo ""
if [[ "$EMBED" -eq 1 ]]; then
  echo "モード: --embed-b64（env に認証値入り。他人に共有しない）"
else
  echo "モード: Secrets 連携（Dashboard Secrets に以下が登録済みなら env は GWS_CONFIG_DIR のみ）"
  echo "  GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET"
  echo "  GWS_CREDENTIALS_PICKLE_B64_PERSONAL"
fi
echo ""
echo "次の操作（手動・1回）:"
echo "1. open https://cursor.com/dashboard/integrations"
echo "2. MCP → Add / Edit → 上記 JSON の mcpServers 全体を貼る"
echo "3. セッション開始時 MCP トグルで両方 ON"
echo ""
echo "埋め込み版が必要なら: bash scripts/generate-dashboard-mcp-json.sh --embed-b64"
