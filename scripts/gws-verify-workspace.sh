#!/usr/bin/env bash
# 北極星 L1-L3: ワークスペース全体のローカル GWS 完了判定
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
FAIL=0

echo "=== GWS ワークスペース検証（北極星 L1-L3） ==="

for profile in aircloset personal; do
  if python3 scripts/gws-verify-profile.py "$profile" >/tmp/gws-verify-"$profile".json 2>/tmp/gws-verify-"$profile".err; then
    echo "✅ L?: $profile OK — $(python3 -c "import json; print(json.load(open('/tmp/gws-verify-$profile.json'))['email'])" 2>/dev/null || true)"
  else
    echo "❌ $profile NG"
    cat /tmp/gws-verify-"$profile".err
    FAIL=1
  fi
done

if [[ -f "${HOME}/.cursor/mcp.json" ]] && grep -q google-workspace-aircloset "${HOME}/.cursor/mcp.json" 2>/dev/null; then
  echo "✅ L3: ~/.cursor/mcp.json にデュアル GWS MCP あり"
else
  echo "❌ L3: ~/.cursor/mcp.json 未設定 → python3 scripts/sync-cursor-mcp-json.py"
  FAIL=1
fi

if [[ "$FAIL" -eq 0 ]]; then
  echo ""
  echo "ローカル基盤 OK。Cloud は: bash scripts/cloud-agent-ui-launch.sh"
  exit 0
fi
echo ""
echo "ローカル NG — bash scripts/gws-heal.sh --visual"
exit 1
