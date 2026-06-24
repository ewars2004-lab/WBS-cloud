#!/usr/bin/env bash
# Generate base64 pickle secrets for Cursor Cloud Agents (both profiles).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${REPO_ROOT}/.local"
mkdir -p "$OUT"

write_secret() {
  local name="$1" pickle="$2" out_file="$3"
  if [[ ! -f "$pickle" ]]; then
    echo "SKIP $name: $pickle not found (run: scripts/gws-oauth-login.sh ...)" >&2
    return 1
  fi
  base64 < "$pickle" | tr -d '\n' > "$out_file"
  echo "OK $name → $out_file ($(wc -c < "$out_file") bytes)"
}

write_secret "GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET" \
  "${HOME}/.config/gws-aircloset/python-credentials.pickle" \
  "${OUT}/GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET.txt" || true

write_secret "GWS_CREDENTIALS_PICKLE_B64_PERSONAL" \
  "${HOME}/.config/gws/python-credentials.pickle" \
  "${OUT}/GWS_CREDENTIALS_PICKLE_B64_PERSONAL.txt" || true

echo "Dashboard: https://cursor.com/dashboard/cloud-agents → Secrets"
echo "  GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET  (r.yaguchi@)"
echo "  GWS_CREDENTIALS_PICKLE_B64_PERSONAL   (ewars2004@)"
