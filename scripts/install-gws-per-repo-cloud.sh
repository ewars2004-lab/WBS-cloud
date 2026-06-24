#!/usr/bin/env bash
# 各 step-rope リポに Cloud GWS スクリプトを配布（cloud-install + verify-gws-cloud）
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WBS="$REPO_ROOT"

TARGETS=(
  "${HOME}/Projects/step-rope/slide-team"
  "${HOME}/Projects/step-rope/shuri-team"
  "${HOME}/Projects/step-rope/teion-team"
)

for dir in "${TARGETS[@]}"; do
  if [[ ! -d "$dir" ]]; then
    echo "SKIP: $dir"
    continue
  fi
  mkdir -p "${dir}/scripts"
  cp "${WBS}/scripts/cloud-install.sh" "${dir}/scripts/cloud-install.sh"
  cp "${WBS}/scripts/verify-gws-cloud.sh" "${dir}/scripts/verify-gws-cloud.sh"
  chmod +x "${dir}/scripts/cloud-install.sh" "${dir}/scripts/verify-gws-cloud.sh"
  echo "✅ ${dir}/scripts/cloud-install.sh"
  echo "✅ ${dir}/scripts/verify-gws-cloud.sh"
done

echo ""
echo "各リポ AGENTS.md / docs に次を追記済みか確認:"
echo "  bash scripts/cloud-install.sh && bash scripts/verify-gws-cloud.sh"
