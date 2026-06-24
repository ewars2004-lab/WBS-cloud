#!/usr/bin/env bash
# Cloud Agents API で WBS-cloud を起動（Dashboard Secret/MCP 手動登録をバイパス）
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

API_KEY_FILE="${CURSOR_API_KEY_FILE:-${HOME}/.config/cursor/cloud-api-key}"
PAYLOAD_FILE="${REPO_ROOT}/.local/cloud-agent-launch-payload.json"
MODE="${1:-verify}"

read_api_key() {
  if [[ -n "${CURSOR_API_KEY:-}" ]]; then
    printf '%s' "$CURSOR_API_KEY"
    return
  fi
  if [[ -f "$API_KEY_FILE" ]]; then
    tr -d ' \n\r' < "$API_KEY_FILE"
    return
  fi
  echo ""
}

ensure_payload() {
  bash "${REPO_ROOT}/scripts/prepare-dual-secrets.sh" >/dev/null 2>&1 || true
  python3 "${REPO_ROOT}/scripts/build-cloud-agent-payload.py" > "$PAYLOAD_FILE"
  echo "✅ payload: $PAYLOAD_FILE"
}

api_key="$(read_api_key)"

case "$MODE" in
  verify)
    ensure_payload
    echo ""
    echo "=== API キー確認 ==="
    if [[ -z "$api_key" ]]; then
      echo "❌ CURSOR_API_KEY 未設定"
      echo "  bash scripts/gws-bootstrap-all.sh   # API key 自動取得を含む"
      exit 1
    fi
    echo "✅ API key: ${API_KEY_FILE}"
    curl -sS "https://api.cursor.com/v1/me" -u "${api_key}:" | python3 -m json.tool
    ;;

  launch)
    ensure_payload
    if [[ -z "$api_key" ]]; then
      echo "ERROR: set CURSOR_API_KEY or ${API_KEY_FILE}" >&2
      exit 1
    fi
    echo "🚀 Launching Cloud Agent (envVars + mcpServers 同梱 → Dashboard 不要)..."
    resp="$(curl -sS -w "\n__HTTP__%{http_code}" \
      -X POST "https://api.cursor.com/v1/agents" \
      -u "${api_key}:" \
      -H "Content-Type: application/json" \
      --data-binary @"${PAYLOAD_FILE}")"
    body="${resp%%__HTTP__*}"
    code="${resp##*__HTTP__}"
    echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
    if [[ "$code" != "200" && "$code" != "201" ]]; then
      echo "HTTP $code" >&2
      exit 1
    fi
    agent_id="$(echo "$body" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('agent',{}).get('id','') or d.get('id',''))" 2>/dev/null || true)"
    if [[ -n "$agent_id" ]]; then
      echo ""
      echo "Agent: https://cursor.com/agents/${agent_id}"
      open "https://cursor.com/agents/${agent_id}" 2>/dev/null || true
    fi
    ;;

  payload)
    ensure_payload
    cat "$PAYLOAD_FILE"
    ;;

  *)
    echo "Usage: $0 [verify|launch|payload]" >&2
    exit 1
    ;;
esac
