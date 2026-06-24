#!/usr/bin/env bash
# ワンショット入口
#   デフォルト: ローカル基盤のみ（北極星 L1-L3）
#   --cloud-ui: Dashboard 確認 + Cloud Agent UI 起動（API キー不要）
set -euo pipefail
DIR="$(dirname "$0")"
if [[ "${1:-}" == "--cloud-ui" ]]; then
  exec "${DIR}/gws-heal.sh" --visual --cloud-ui "${@:2}"
fi
exec "${DIR}/gws-heal.sh" --visual "$@"
