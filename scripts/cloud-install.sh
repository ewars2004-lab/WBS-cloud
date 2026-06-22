#!/usr/bin/env bash
# Cloud Agent VM 起動時: 依存関係 + Google 認証 pickle を Secrets から展開
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_DIR="${GWS_CONFIG_DIR:-${HOME}/.config/gws-aircloset}"
TOKEN_FILE="${CONFIG_DIR}/python-credentials.pickle"

pip3 install --quiet google-auth google-auth-oauthlib google-api-python-client

chmod +x "${ROOT}/scripts/"*.sh 2>/dev/null || true
chmod +x "${ROOT}/scripts/"*.py 2>/dev/null || true

mkdir -p "${CONFIG_DIR}"

if [[ -n "${GWS_CREDENTIALS_PICKLE_B64:-}" ]]; then
  echo "${GWS_CREDENTIALS_PICKLE_B64}" | base64 -d > "${TOKEN_FILE}"
  echo "cloud-install: Google credentials restored from GWS_CREDENTIALS_PICKLE_B64"
elif [[ -f "${TOKEN_FILE}" ]]; then
  echo "cloud-install: using existing ${TOKEN_FILE}"
else
  echo "cloud-install: WARN — no Google credentials (set Secret GWS_CREDENTIALS_PICKLE_B64 or register Sheets MCP env)"
fi

if [[ -n "${GWS_CLIENT_SECRET_JSON:-}" ]]; then
  printf '%s' "${GWS_CLIENT_SECRET_JSON}" > "${CONFIG_DIR}/client_secret.json"
fi
