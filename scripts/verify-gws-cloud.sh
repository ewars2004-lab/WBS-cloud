#!/usr/bin/env bash
# Cloud VM: Dashboard Secrets → pickle 展開 + 両プロファイル検証（リポ内スクリプトのみ・プラットフォームリポ不要）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FAIL=0

echo "=== GWS Cloud 検証（デュアル・workspace 共通） ==="

check_secret() {
  local name="$1"
  local val="${!name:-}"
  if [[ -n "$val" ]]; then
    echo "✅ ${name}: 設定済み (len=${#val})"
  else
    echo "❌ ${name}: 未設定"
    echo "   → Dashboard → Cloud Agents → Secrets"
    FAIL=1
  fi
}

check_secret GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET
check_secret GWS_CREDENTIALS_PICKLE_B64_PERSONAL

echo ""
echo "--- cloud-install ---"
if [[ -f scripts/cloud-install.sh ]]; then
  bash scripts/cloud-install.sh || FAIL=1
else
  echo "❌ scripts/cloud-install.sh がありません"
  FAIL=1
fi

verify_py="${ROOT}/scripts/gws-verify-profile.py"
if [[ ! -f "$verify_py" ]]; then
  echo "❌ gws-verify-profile.py がこのリポにありません"
  echo "   Mac で: bash ~/Projects/cursor-gws-platform/scripts/install-gws-per-repo-cloud.sh"
  exit 1
fi

echo ""
echo "--- gws-verify aircloset ---"
if GWS_CONFIG_DIR="${HOME}/.config/gws-aircloset" python3 "$verify_py" aircloset; then
  echo "✅ aircloset GWS OK"
else
  FAIL=1
fi

echo ""
echo "--- gws-verify personal ---"
if GWS_CONFIG_DIR="${HOME}/.config/gws" python3 "$verify_py" personal; then
  echo "✅ personal GWS OK"
else
  FAIL=1
fi

if [[ "$FAIL" -eq 0 ]]; then
  echo ""
  echo "GWS 検証OK（aircloset + personal）"
  exit 0
fi
echo ""
echo "GWS 検証NG"
exit 1
