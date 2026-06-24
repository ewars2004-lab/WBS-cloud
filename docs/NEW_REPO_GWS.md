# 新リポジトリ向け GWS ブートストラップ

新しい step-rope リポジトリでも **同じ2アカウント・2 MCP** を使う。リポジトリごとに OAuth や MCP JSON を複製しない。

## やること（リポジトリ側）

1. README または `docs/MCP_SETUP.md` に1行追記:

   > Google Workspace: [WBS-cloud/docs/GWS_DUAL_ACCOUNT.md](https://github.com/ewars2004-lab/WBS-cloud/blob/main/docs/GWS_DUAL_ACCOUNT.md)

2. **`.cursor/mcp.json` は作らない**（グローバル `~/.cursor/mcp.json` が正本）

3. Cloud Agent を使う場合、リポジトリ固有の Secret は不要。Dashboard の workspace 共通 Secret をそのまま使う:
   - `GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET`
   - `GWS_CREDENTIALS_PICKLE_B64_PERSONAL`

4. Cloud で GWS MCP が必要なら、WBS-cloud と同じ Integrations 設定（`dashboard-mcp-dual.json`）を Dashboard に1回登録済みで足りる。

4. Cloud で GWS を使うリポには `install-gws-per-repo-cloud.sh` で `cloud-install.sh` / `verify-gws-cloud.sh` を配布済みにする。

## やること（Mac 初回のみ・全リポジトリ共通）

```bash
cd ~/Projects/WBS-cloud
bash scripts/install-gws-mcp.sh
bash scripts/gws-oauth-login.sh aircloset
bash scripts/gws-oauth-login.sh personal
python3 scripts/gws-verify-profile.py aircloset
python3 scripts/gws-verify-profile.py personal
```

Cursor 再起動後、User Rule を貼る: `docs/CURSOR_USER_RULE_GWS.md`

## アカウントの選び方

| 用途 | MCP |
|------|-----|
| WBS・社内シート・air-closet 共有 | `google-workspace-aircloset` |
| 個人 Drive / Docs / ewars2004 | `google-workspace-personal` |

403 や「ファイルが見つからない」→ もう一方の MCP を試す。不明なら `drive_about`。

## Cloud Agent 起動時

リポジトリに `scripts/cloud-install.sh` を置く場合は WBS-cloud のものをコピーするか、起動プロンプトで次を実行:

```bash
bash scripts/cloud-install.sh   # WBS-cloud にある場合
bash scripts/verify-cloud-ready.sh  # WBS-cloud のみ
```

他リポジトリは Dashboard Secrets + Integrations が既にあれば、エージェントが MCP を直接使える。
