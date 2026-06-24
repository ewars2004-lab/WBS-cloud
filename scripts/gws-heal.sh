#!/usr/bin/env bash
# verify 駆動の GWS 環境 heal（ローカル + 任意で Cloud）
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

DO_CLOUD=0
DO_PUSH=0
DO_VISUAL=0
for arg in "$@"; do
  case "$arg" in
    --cloud) DO_CLOUD=1 ;;
    --push) DO_PUSH=1 ;;
    --visual) DO_VISUAL=1 ;;
  esac
done

if [[ "$DO_VISUAL" -eq 1 ]]; then
  export GWS_VISUAL=1
fi

API_KEY_FILE="${HOME}/.config/cursor/cloud-api-key"
STATE_DIR="${REPO_ROOT}/.local/heal"
mkdir -p "$STATE_DIR"

log() { echo "[gws-heal] $*" ; }

verify_profile() {
  python3 scripts/gws-verify-profile.py "$1" >/dev/null 2>&1
}

heal_profile() {
  local profile="$1"
  if verify_profile "$profile"; then
    log "✅ verify OK: $profile"
    return 0
  fi
  log "⚠️ verify NG: $profile → 再 OAuth"
  bash scripts/gws-oauth-login.sh "$profile" || true
  if verify_profile "$profile"; then
    log "✅ verify OK after OAuth: $profile"
    return 0
  fi
  log "TIER3: Google アカウント選択/2FA が必要: $profile"
  log "  完了したら: GWS_HEAL_CONTINUE=1 bash scripts/gws-heal.sh $*"
  return 2
}

heal_api_key() {
  if [[ -n "${CURSOR_API_KEY:-}" ]] || [[ -f "$API_KEY_FILE" && -s "$API_KEY_FILE" ]]; then
    log "✅ API key あり"
    return 0
  fi
  if [[ "${GWS_VISUAL:-}" == "1" ]]; then
    log "👁 Chrome を開きます（Cursor | Chrome 画面分割推奨）"
    log "👁 Integrations → Cloud Agents API キー作成を自動操作します"
  fi
  log "API key 取得を試行…"
  python3 scripts/chrome-api-key-setup.py || true
  if [[ -f "$API_KEY_FILE" && -s "$API_KEY_FILE" ]]; then
    return 0
  fi
  rc=0
  python3 scripts/gws-ui-agent.py api_key || rc=$?
  if [[ -f "$API_KEY_FILE" && -s "$API_KEY_FILE" ]]; then
    return 0
  fi
  if [[ "$rc" -eq 2 ]]; then
    return 2
  fi
  log "TIER3: Cursor ログイン/指紋後にチャットで「続けて」"
  return 2
}

heal_local() {
  log "=== Phase: 依存 ==="
  pip3 install --quiet -r requirements.txt
  python3 -c "import playwright" 2>/dev/null || pip3 install --quiet playwright
  python3 -m playwright install chromium 2>/dev/null || true

  log "=== Phase: MCP ランチャー ==="
  bash scripts/install-gws-mcp.sh

  log "=== Phase: OAuth verify ==="
  heal_profile aircloset || return $?
  heal_profile personal || return $?

  log "=== Phase: mcp.json / rules ==="
  python3 scripts/sync-cursor-mcp-json.py
  bash scripts/install-gws-cursor-rules.sh

  log "=== Phase: secrets ファイル ==="
  bash scripts/prepare-dual-secrets.sh

  log "=== Phase: CLI verify ==="
  GWS_CONFIG_DIR="${HOME}/.config/gws-aircloset" python3 scripts/sheets-cli.py verify >/dev/null
  log "✅ ローカル heal 完了"
  return 0
}

heal_git_push() {
  if [[ "$DO_PUSH" -ne 1 ]]; then
    log "skip push (--push 未指定)"
    return 0
  fi
  log "=== Phase: git pull / commit / push ==="
  git fetch origin
  if git rev-parse --verify origin/main >/dev/null 2>&1; then
    git pull --rebase origin main || git pull origin main || true
  fi
  git add -A
  if git diff --cached --quiet; then
    log "commit する変更なし"
  else
    git commit -m "$(cat <<'EOF'
Add dual GWS platform: heal, ui-agent, and cloud bootstrap.

Unify aircloset/personal OAuth, MCP, and verify-driven recovery for all repos.
EOF
)"
  fi
  git push -u origin HEAD
  log "✅ push 完了"
}

heal_cloud() {
  log "=== Phase: API key ==="
  heal_api_key || return $?

  log "=== Phase: Cloud launch ==="
  bash scripts/launch-wbs-cloud-agent.sh verify
  bash scripts/launch-wbs-cloud-agent.sh launch | tee "${STATE_DIR}/last-launch.json"
  python3 - <<'PY' "${STATE_DIR}/status.json"
import json, sys, time
from pathlib import Path
p = Path(sys.argv[1])
p.write_text(json.dumps({
  "phase": "cloud_launched",
  "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
  "agents_url": "https://cursor.com/agents",
}, indent=2) + "\n", encoding="utf-8")
PY
  log "Cloud Agent 起動済み。VM 上で verify-cloud-ready が走る想定。"
  log "結果: https://cursor.com/agents"
  return 0
}

# --- main ---
if [[ "${GWS_HEAL_CONTINUE:-}" == "1" ]]; then
  log "続行モード（Tier3 後）"
fi

heal_local || exit $?

if [[ "$DO_CLOUD" -eq 1 ]]; then
  heal_git_push || exit $?
  heal_cloud || exit $?
fi

log "=== heal 成功 ==="
exit 0
