#!/usr/bin/env bash
# 視覚モード用ログ（Chrome 横で手順を追う）
vlog() {
  if [[ "${GWS_VISUAL:-}" == "1" ]]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "👁  $*"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  fi
}

step() {
  if [[ "${GWS_VISUAL:-}" == "1" ]]; then
    echo "[手順] $*"
  else
    echo "[gws] $*"
  fi
}
