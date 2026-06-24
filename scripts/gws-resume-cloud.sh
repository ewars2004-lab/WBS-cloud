#!/usr/bin/env bash
# API キー取得 + Cloud 起動だけ再開（視覚モード）
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
# shellcheck source=scripts/gws-visual.sh
source "${REPO_ROOT}/scripts/gws-visual.sh"

export GWS_VISUAL=1
export GWS_CHROME_FORCE_SYNC=1
export GWS_HEAL_CONTINUE=1

vlog "再開: API キー → Cloud Agent 起動"
vlog "Cursor | Chrome を画面分割推奨"

API_KEY_FILE="${HOME}/.config/cursor/cloud-api-key"
if [[ ! -s "$API_KEY_FILE" ]]; then
  step "API キー取得（Chrome で Integrations を操作）"
  python3 scripts/chrome-api-key-setup.py || true
  if [[ ! -s "$API_KEY_FILE" ]]; then
    python3 scripts/gws-ui-agent.py api_key || true
  fi
fi

if [[ ! -s "$API_KEY_FILE" ]]; then
  echo "[gws-resume] TIER3: キー作成後「続けて」"
  exit 2
fi

step "Cloud Agent API 起動"
bash scripts/launch-wbs-cloud-agent.sh verify
bash scripts/launch-wbs-cloud-agent.sh launch
vlog "Agent 進捗: https://cursor.com/agents"
