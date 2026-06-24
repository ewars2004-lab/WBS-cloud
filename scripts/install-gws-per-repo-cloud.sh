#!/usr/bin/env bash
# 各リポに Cloud GWS スクリプトを配布（WBS-cloud クローン不要で VM 検証可）
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WBS="$REPO_ROOT"

TARGETS=(
  "${HOME}/Projects/step-rope/slide-team"
  "${HOME}/Projects/step-rope/shuri-team"
  "${HOME}/Projects/step-rope/teion-team"
)

BUNDLE=(
  cloud-install.sh
  verify-gws-cloud.sh
  gws-verify-profile.py
  gws-python-mcp.py
  gws_credentials.py
)

for dir in "${TARGETS[@]}"; do
  if [[ ! -d "$dir" ]]; then
    echo "SKIP: $dir"
    continue
  fi
  mkdir -p "${dir}/scripts"
  for f in "${BUNDLE[@]}"; do
    src="${WBS}/scripts/${f}"
    dest="${dir}/scripts/${f}"
    if [[ ! -f "$src" ]]; then
      echo "SKIP missing: $src"
      continue
    fi
    cp "$src" "$dest"
    chmod +x "$dest" 2>/dev/null || true
    echo "✅ ${dest}"
  done
done

echo ""
echo "各リポは WBS-cloud なしで verify-gws-cloud.sh が動きます。"
