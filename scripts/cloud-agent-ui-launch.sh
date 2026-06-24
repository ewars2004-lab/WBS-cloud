#!/usr/bin/env bash
# Cloud: Dashboard Secrets 確認（デフォルト）。--launch で UI 起動（1回だけ手動確認推奨）
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
# shellcheck source=scripts/gws-visual.sh
source "${REPO_ROOT}/scripts/gws-visual.sh"

export GWS_VISUAL=1
REPO_SLUG="${GWS_CLOUD_VERIFY_REPO:-ewars2004-lab/WBS-cloud}"

if [[ "${1:-}" == "--launch" ]]; then
  vlog "Cloud Agent を UI から1本起動（リポ: ${REPO_SLUG}）"
  python3 scripts/cloud-agent-ui-launch.py --repo "$REPO_SLUG"
else
  vlog "Dashboard Secrets のみ確認（Agent は起動しません）"
  python3 scripts/cloud-agent-ui-launch.py --secrets-only || exit $?
  echo ""
  echo "Cloud 検証を起動する場合（手動推奨）:"
  echo "  1. open https://cursor.com/agents"
  echo "  2. 新人エージェント → ${REPO_SLUG}"
  echo "  3. bash scripts/cloud-install.sh && bash scripts/verify-cloud-ready.sh"
  echo ""
  echo "自動1本: bash scripts/cloud-agent-ui-launch.sh --launch"
fi
