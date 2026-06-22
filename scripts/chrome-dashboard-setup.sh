#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
"${REPO_ROOT}/scripts/setup-cloud-complete.sh" >/dev/null 2>&1 || true
python3 "${REPO_ROOT}/scripts/chrome-dashboard-setup.py"
