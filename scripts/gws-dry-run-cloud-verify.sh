#!/usr/bin/env bash
# Cloud VM と同じ Secret → cloud-install → verify をローカルで再現（Agent 起動不要）
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

bash scripts/prepare-dual-secrets.sh >/dev/null
export GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET="$(tr -d '\n' < .local/GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET.txt)"
export GWS_CREDENTIALS_PICKLE_B64_PERSONAL="$(tr -d '\n' < .local/GWS_CREDENTIALS_PICKLE_B64_PERSONAL.txt)"

echo "=== Cloud 経路ドライラン（Dashboard Secrets と同じ値） ==="
bash scripts/verify-cloud-ready.sh
