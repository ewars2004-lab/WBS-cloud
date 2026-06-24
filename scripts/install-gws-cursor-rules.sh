#!/usr/bin/env bash
# Install GWS rules into WBS-cloud + step-rope repos.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RULES=(
  "gws-dual-account.mdc"
  "gws-platform-goal.mdc"
)

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
  for rule in "${RULES[@]}"; do
    src="${REPO_ROOT}/.cursor/rules/${rule}"
    dest="${dir}/.cursor/rules/${rule}"
    if [[ ! -f "$src" ]]; then
      echo "SKIP (no src): $src"
      continue
    fi
    if [[ "$(cd "$dir" && pwd)" == "$(cd "$REPO_ROOT" && pwd)" ]]; then
      echo "✅ (source) $dest"
      continue
    fi
    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
    echo "✅ $dest"
  done
done
