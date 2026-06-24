#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_SRC="$REPO_ROOT/skills"
SKILLS_DST="${CURSOR_SKILLS_DIR:-$HOME/.cursor/skills}"

echo "==> WBS-cloud bootstrap ($REPO_ROOT)"

if ! command -v python3 >/dev/null; then
  echo "ERROR: python3 が必要です" >&2
  exit 1
fi

python3 -m venv "$REPO_ROOT/.venv" 2>/dev/null || true
# shellcheck disable=SC1091
source "$REPO_ROOT/.venv/bin/activate"
pip install -q -U pip
pip install -q -r "$REPO_ROOT/requirements.txt"

mkdir -p "$SKILLS_DST"
for skill in "$SKILLS_SRC"/*/; do
  name="$(basename "$skill")"
  target="$SKILLS_DST/$name"
  if [ -L "$target" ] || [ -d "$target" ]; then
    rm -rf "$target"
  fi
  ln -sf "$skill" "$target"
  echo "  linked skill: $name"
done

mkdir -p "$REPO_ROOT/state/inbox"

echo "==> doctor"
python3 -m wbs_engine.runner doctor

echo ""
echo "完了。次のコマンド:"
echo "  cd $REPO_ROOT && source .venv/bin/activate"
echo "  python3 -m wbs_engine.runner validate     # ユニットテスト"
echo "  python3 -m wbs_engine.runner run        # dry-run（本番WBS）"
echo "  python3 -m wbs_engine.runner run --apply  # 書込（要Google認証）"
echo ""
echo "Google認証: MCP_SETUP.md を参照"
