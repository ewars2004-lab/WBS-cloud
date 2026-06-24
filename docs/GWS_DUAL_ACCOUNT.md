# デュアル Google Workspace MCP（全リポジトリ共通）

## アカウント

| MCP 名 | プロファイル | 想定メール |
|--------|-------------|-----------|
| `google-workspace-aircloset` | aircloset | `r.yaguchi@air-closet.com` |
| `google-workspace-personal` | personal | `ewars2004@gmail.com` |

設定の正本: **`~/.cursor/mcp.json`**（リポジトリごとではない）

## 初回セットアップ（Mac で1回）

**ワンショット（推奨）:**

```bash
cd ~/Projects/WBS-cloud
bash scripts/gws-bootstrap-all.sh
```

手動ステップの説明: [docs/GWS_ONE_SHOT.md](GWS_ONE_SHOT.md)

<details>
<summary>個別コマンド（従来）</summary>

```bash
bash scripts/install-gws-mcp.sh
bash scripts/gws-oauth-login.sh aircloset
bash scripts/gws-oauth-login.sh personal
python3 scripts/gws-verify-profile.py aircloset
python3 scripts/gws-verify-profile.py personal
```

</details>

Cursor を再起動（または Reload Window）。

## 使える API

両 MCP とも: **Sheets / Google Slides / Docs / Drive / Calendar**

## エージェントへの指示（User Rule 推奨）

- 社内 WBS・air-closet 共有シート → `user-google-workspace-aircloset`
- 個人・ewars2004 のファイル → `user-google-workspace-personal`
- 不明なら `drive_about` でメールを確認してから操作

## Cloud Agent Secrets

```bash
bash scripts/prepare-dual-secrets.sh
```

Dashboard → **Cloud Agents → Secrets** に2つ登録:

- `GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET`
- `GWS_CREDENTIALS_PICKLE_B64_PERSONAL`

## Cloud Agent MCP Integrations

```bash
bash scripts/generate-dashboard-mcp-json.sh
# → .local/dashboard-mcp-dual.json を Dashboard → Integrations → MCP に貼る
```

一括セットアップ: `bash scripts/setup-cloud-complete.sh`

Cloud 起動後: `bash scripts/verify-cloud-ready.sh`

## 新リポジトリ

`docs/NEW_REPO_GWS.md` — リポジトリごとに OAuth/MCP を複製しない手順

## トークン更新

```bash
bash scripts/gws-oauth-login.sh aircloset   # または personal
bash scripts/prepare-dual-secrets.sh
# Dashboard Secrets を更新 → Agent 再起動
```
