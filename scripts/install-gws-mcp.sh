#!/usr/bin/env bash
# Install global MCP wrapper scripts for both Google accounts.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BIN="${HOME}/.local/bin"
mkdir -p "$BIN"

for pair in "aircloset-gws-mcp:gws-aircloset:8092" "personal-gws-mcp:gws:8093"; do
  name="${pair%%:*}"
  rest="${pair#*:}"
  cfg="${rest%%:*}"
  port="${rest##*:}"
  target="${BIN}/${name}"
  cat > "$target" <<EOF
#!/usr/bin/env bash
export GWS_CONFIG_DIR="\${HOME}/.config/${cfg}"
export GWS_OAUTH_PORT=${port}
exec python3 "${REPO_ROOT}/scripts/gws-python-mcp.py"
EOF
  chmod +x "$target"
  echo "installed: $target"
done

# Backward compat: aircloset sheets MCP name
ln -sf "${BIN}/aircloset-gws-mcp" "${BIN}/aircloset-sheets-mcp"

echo ""
echo "Next: ~/.cursor/mcp.json を更新後、Cursor を再起動"
echo "  bash scripts/gws-oauth-login.sh aircloset   # r.yaguchi@"
echo "  bash scripts/gws-oauth-login.sh personal    # ewars2004@"
