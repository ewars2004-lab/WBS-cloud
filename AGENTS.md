# Cloud Agent 起動時の検証

WBS-cloud を Cloud Agent で開いたら、まず:

```bash
bash scripts/verify-cloud-ready.sh
```

## 前提（Dashboard で1回設定）

| 項目 | 内容 |
|------|------|
| Secrets | `GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET`, `GWS_CREDENTIALS_PICKLE_B64_PERSONAL` |
| MCP Integrations | `.local/dashboard-mcp-dual.json`（`bash scripts/generate-dashboard-mcp-json.sh` で生成） |
| Slack | Dashboard で Connect 済み |

セットアップ手順: `bash scripts/setup-cloud-complete.sh`

## 成功の目安

- 両 Secret が設定済み
- `gws-verify-profile.py` が aircloset / personal とも OK
- `sheets-cli.py verify` が WBS スプレッドシートを読める

## Google Workspace ルーティング

`docs/CURSOR_USER_RULE_GWS.md` を Cursor User Rules に貼る。

詳細: `docs/GWS_DUAL_ACCOUNT.md`, `docs/NEW_REPO_GWS.md`
