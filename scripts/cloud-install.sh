#!/usr/bin/env bash
# Cloud Agent VM 起動時: 依存関係 + 両プロファイルの Google 認証 pickle を Secrets から展開
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

pip3 install --quiet google-auth google-auth-oauthlib google-api-python-client

chmod +x "${ROOT}/scripts/"*.sh 2>/dev/null || true
chmod +x "${ROOT}/scripts/"*.py 2>/dev/null || true

restore_profile() {
  local config_dir="$1"
  local secret_env="$2"
  local token_file="${config_dir}/python-credentials.pickle"
  local b64=""

  mkdir -p "${config_dir}"

  # shellcheck disable=SC2154
  if [[ -n "${!secret_env:-}" ]]; then
    b64="${!secret_env}"
  elif [[ "${secret_env}" == "GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET" && -n "${GWS_CREDENTIALS_PICKLE_B64:-}" ]]; then
    b64="${GWS_CREDENTIALS_PICKLE_B64}"
  fi

  if [[ -n "${b64}" ]]; then
    echo "${b64}" | base64 -d > "${token_file}"
    echo "cloud-install: restored ${token_file} from ${secret_env}"
  elif [[ -f "${token_file}" ]]; then
    echo "cloud-install: using existing ${token_file}"
  else
    echo "cloud-install: WARN — no credentials for ${config_dir} (set Secret ${secret_env})"
  fi

  if [[ -n "${GWS_CLIENT_SECRET_JSON:-}" && ! -f "${config_dir}/client_secret.json" ]]; then
    printf '%s' "${GWS_CLIENT_SECRET_JSON}" > "${config_dir}/client_secret.json"
  fi
}

restore_profile "${HOME}/.config/gws-aircloset" "GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET"
restore_profile "${HOME}/.config/gws" "GWS_CREDENTIALS_PICKLE_B64_PERSONAL"
