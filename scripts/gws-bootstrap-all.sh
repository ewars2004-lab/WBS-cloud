#!/usr/bin/env bash
# ワンショット入口 → gws-heal（視覚モード + Cloud + push）
exec "$(dirname "$0")/gws-heal.sh" --visual --cloud --push "$@"
