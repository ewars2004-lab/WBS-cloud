#!/usr/bin/env bash
# Cloud Agent: run from repo root so stdio MCP resolves scripts/ correctly.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
exec python3 "$ROOT/scripts/aircloset-sheets-mcp-cloud.py"
