#!/usr/bin/env bash
# verify 駆動の GWS 環境 heal（ローカル + 任意で Cloud）
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
# shellcheck source=scripts/gws-visual.sh
source "${REPO_ROOT}/scripts/gws-visual.sh"

DO_CLOUD=0
DO_CLOUD_UI=0
DO_PUSH=0
DO_VISUAL=0
for arg in "$@"; do
  case "$arg" in
    --cloud) DO_CLOUD=1 ;;
    --cloud-ui) DO_CLOUD_UI=1 ;;
    --push) DO_PUSH=1 ;;
    --visual) DO_VISUAL=1 ;;
  esac
done

if [[ "$DO_VISUAL" -eq 1 ]]; then
  export GWS_VISUAL=1
  export GWS_CHROME_FORCE_SYNC=1
  vlog "視覚モード: Cursor と Chrome を画面分割すると手順が見えます"
  vlog "Chrome 136+ の制約: ログイン済みコピープロファイルで Dashboard を開きます"
fi

API_KEY_FILE="${HOME}/.config/cursor/cloud-api-key"
STATE_DIR="${REPO_ROOT}/.local/heal"
mkdir -p "$STATE_DIR"

log() { echo "[gws-heal] $*" ; }

verify_profile() {
  if [[ "${GWS_VISUAL:-}" == "1" ]]; then
    python3 scripts/gws-verify-profile.py "$1"
  else
    python3 scripts/gws-verify-profile.py "$1" >/dev/null 2>&1
  fi
}

heal_profile() {
  local profile="$1"
  step "Google プロファイル '${profile}' を検証します"
  if python3 scripts/gws-verify-profile.py "$1" >/dev/null 2>&1; then
    log "✅ verify OK: $profile"
    return 0
  fi
  vlog "認証が切れています → ブラウザで Google 再ログインします（${profile} のアカウントを選んでください）"
  bash scripts/gws-oauth-login.sh "$profile" || true
  if python3 scripts/gws-verify-profile.py "$1" >/dev/null 2>&1; then
    log "✅ verify OK after OAuth: $profile"
    return 0
  fi
  log "TIER3: Google アカウント選択/2FA が必要: $profile → 完了したら「続けて」"
  return 2
}

heal_api_key() {
  if [[ -n "${CURSOR_API_KEY:-}" ]] || [[ -f "$API_KEY_FILE" && -s "$API_KEY_FILE" ]]; then
    log "✅ API key あり"
    return 0
  fi
  vlog "Cursor Dashboard → Integrations を開きます"
  vlog "Cloud Agents API キーを作成して ~/.config/cursor/cloud-api-key に保存します"
  step "Chrome 起動（未保存のタブがある場合は先に保存してください）"
  python3 scripts/chrome-api-key-setup.py || true
  if [[ -f "$API_KEY_FILE" && -s "$API_KEY_FILE" ]]; then
    vlog "API キー取得完了"
    return 0
  fi
  rc=0
  python3 scripts/gws-ui-agent.py api_key || rc=$?
  if [[ -f "$API_KEY_FILE" && -s "$API_KEY_FILE" ]]; then
    return 0
  fi
  log "TIER3: Cursor ログイン/指紋 → 完了したら「続けて」"
  return 2
}

heal_local() {
  step "Phase 1/6: 依存パッケージ"
  pip3 install --quiet -r requirements.txt
  python3 -c "import playwright" 2>/dev/null || pip3 install --quiet playwright
  python3 -m playwright install chromium 2>/dev/null || true

  step "Phase 2/6: MCP ランチャー（~/.local/bin）"
  bash scripts/install-gws-mcp.sh

  step "Phase 3/6: OAuth 検証（aircloset + personal）"
  heal_profile aircloset || return $?
  heal_profile personal || return $?

  step "Phase 4/6: グローバル mcp.json とルール"
  python3 scripts/sync-cursor-mcp-json.py
  bash scripts/install-gws-cursor-rules.sh

  step "Phase 5/6: Cloud 用 Secret ファイル生成"
  bash scripts/prepare-dual-secrets.sh

  step "Phase 6/6: WBS スプレッドシート読取テスト"
  if [[ "${GWS_VISUAL:-}" == "1" ]]; then
    GWS_CONFIG_DIR="${HOME}/.config/gws-aircloset" python3 scripts/sheets-cli.py verify
  else
    GWS_CONFIG_DIR="${HOME}/.config/gws-aircloset" python3 scripts/sheets-cli.py verify >/dev/null
  fi
  vlog "ローカル GWS は使える状態です"
  log "✅ ローカル heal 完了"
  return 0
}

heal_git_push() {
  if [[ "$DO_PUSH" -ne 1 ]]; then
    log "skip push (--push 未指定)"
    return 0
  fi
  step "GitHub に push（Cloud VM がこのコードを clone します）"
  git fetch origin
  if git rev-parse --verify origin/main >/dev/null 2>&1; then
    git pull --rebase origin main || git pull origin main || true
  fi
  git add -A
  if git diff --cached --quiet; then
    log "commit する変更なし"
  else
    git commit -m "$(cat <<'EOF'
Update GWS heal visual mode and Chrome default profile.
EOF
)"
  fi
  git push -u origin HEAD
  log "✅ push 完了"
}

heal_cloud_ui() {
  step "Cloud: Dashboard Secrets 確認（Agent は自動起動しない）"
  vlog "北極星 C1-C2: docs/GWS_NORTH_STAR.md"
  bash scripts/cloud-agent-ui-launch.sh || return $?
  return 0
}

heal_cloud_api() {
  step "Cloud Phase 1/2: API キー（任意・上級者経路）"
  heal_api_key || return $?

  step "Cloud Phase 2/2: Cloud Agent API 起動"
  vlog "Dashboard は開きません。API に認証+ MCP を同梱して VM を起動します"
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
  vlog "ブラウザで Agent の進捗を確認: https://cursor.com/agents"
  open "https://cursor.com/agents" 2>/dev/null || true
  log "Cloud Agent 起動済み"
  return 0
}

if [[ "${GWS_HEAL_CONTINUE:-}" == "1" ]]; then
  log "続行モード（Tier3 後）"
fi

heal_local || exit $?

if [[ "$DO_CLOUD_UI" -eq 1 ]]; then
  heal_cloud_ui || exit $?
elif [[ "$DO_CLOUD" -eq 1 ]]; then
  heal_git_push || exit $?
  heal_cloud_api || exit $?
fi

bash scripts/gws-verify-workspace.sh >/dev/null && log "✅ 北極星 L1-L3 OK（docs/GWS_NORTH_STAR.md）"
log "=== heal 成功 ==="
exit 0
