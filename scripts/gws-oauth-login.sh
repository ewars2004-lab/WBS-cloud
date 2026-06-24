#!/usr/bin/env bash
# OAuth login for a GWS profile. Opens browser.
# Usage: ./scripts/gws-oauth-login.sh aircloset|personal
set -euo pipefail

PROFILE="${1:-}"
case "$PROFILE" in
  aircloset)
    export GWS_CONFIG_DIR="${HOME}/.config/gws-aircloset"
    export GWS_OAUTH_PORT=8092
    ;;
  personal)
    export GWS_CONFIG_DIR="${HOME}/.config/gws"
    export GWS_OAUTH_PORT=8093
    ;;
  *)
    echo "Usage: $0 aircloset|personal" >&2
    echo "  aircloset → r.yaguchi@air-closet.com (port 8092)" >&2
    echo "  personal  → ewars2004@gmail.com (port 8093)" >&2
    exit 1
    ;;
esac

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PICKLE="${GWS_CONFIG_DIR}/python-credentials.pickle"

if [[ ! -f "${GWS_CONFIG_DIR}/client_secret.json" ]]; then
  echo "ERROR: ${GWS_CONFIG_DIR}/client_secret.json がありません" >&2
  exit 1
fi

echo "==> OAuth: ${PROFILE} (${GWS_CONFIG_DIR})"
echo "    ブラウザで正しい Google アカウントを選んでください。"
rm -f "$PICKLE"

python3 -c "
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('m', Path('${REPO_ROOT}/scripts/gws-python-mcp.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.get_creds()
print('OAuth OK →', mod.TOKEN_FILE)
"

python3 "${REPO_ROOT}/scripts/gws-verify-profile.py" "$PROFILE"
