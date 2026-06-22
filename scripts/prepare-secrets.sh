#!/usr/bin/env bash
# ローカル Mac で実行: Google Sheets 認証を Cursor Cloud Secrets 用に base64 化
set -euo pipefail

PICKLE="${HOME}/.config/gws-aircloset/python-credentials.pickle"

if [[ ! -f "$PICKLE" ]]; then
  echo "ERROR: $PICKLE が見つかりません。" >&2
  echo "先に Desktop で aircloset-sheets-mcp の OAuth を完了してください。" >&2
  exit 1
fi

B64=$(base64 < "$PICKLE" | tr -d '\n')

echo "=== Cursor Dashboard → Cloud Agents → Secrets に追加 ==="
echo ""
echo "Name:  GWS_CREDENTIALS_PICKLE_B64"
echo "Value: (以下をコピー)"
echo ""
echo "$B64"
echo ""
echo "Dashboard: https://cursor.com/dashboard/cloud-agents"
echo ""
echo "追加後、Cloud Agent で sheets_values_get(新NagiWBS!A5:O5) をテストしてください。"
