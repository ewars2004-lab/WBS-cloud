#!/usr/bin/env bash
# Install GWS routing rule into WBS-cloud + step-rope repos (no Settings paste needed).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${REPO_ROOT}/.cursor/rules/gws-dual-account.mdc"

TARGETS=(
  "${REPO_ROOT}"
  "${HOME}/Projects/step-rope/shuri-team"
  "${HOME}/Projects/step-rope/slide-team"
  "${HOME}/Projects/step-rope/teion-team"
)

for dir in "${TARGETS[@]}"; do
  if [[ ! -d "$dir" ]]; then
    echo "SKIP (no dir): $dir"
    continue
  fi
  dest="${dir}/.cursor/rules/gws-dual-account.mdc"
  if [[ "$(cd "$dir" && pwd)" == "$(cd "$REPO_ROOT" && pwd)" ]]; then
    echo "✅ (source) $dest"
    continue
  fi
  mkdir -p "$(dirname "$dest")"
  cp "$SRC" "$dest"
  echo "✅ $dest"
done
