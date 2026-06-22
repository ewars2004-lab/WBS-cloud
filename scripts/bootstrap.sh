#!/usr/bin/env bash
# WBS更新チーム: link Cursor skills to this repo (run on each PC after clone)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CURSOR_SKILLS="$HOME/.cursor/skills"

mkdir -p "$CURSOR_SKILLS"

for name in \
  wbs-update-workflow \
  wbs-update-planner \
  wbs-slack-investigator \
  wbs-update-writer \
  wbs-update-verifier; do
  src="$REPO_ROOT/skills/$name"
  dest="$CURSOR_SKILLS/$name"

  if [[ ! -d "$src" ]]; then
    echo "ERROR: missing $src" >&2
    exit 1
  fi

  if [[ -e "$dest" && ! -L "$dest" ]]; then
    echo "ERROR: $dest exists and is not a symlink. Move aside manually." >&2
    exit 1
  fi

  ln -sfn "$src" "$dest"
  echo "linked: $dest -> $src"
done

echo ""
echo "WBS更新チーム bootstrap OK"
echo "Repo: $REPO_ROOT"
