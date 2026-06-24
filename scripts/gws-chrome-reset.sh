#!/usr/bin/env bash
# 自動化 Chrome プロファイルをリセット（白画面・ログインループ時）
set -euo pipefail
PROFILE="${HOME}/.cursor/wbs-chrome-profile"
echo "自動化 Chrome プロファイルを削除: ${PROFILE}"
rm -rf "${PROFILE}"
echo "✅ リセット完了"
echo "次: bash scripts/gws-heal.sh --visual --cloud --push"
echo "  または普段の Chrome で https://cursor.com/dashboard?tab=integrations を開く"
