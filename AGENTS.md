# GWS プラットフォーム（全リポ共通）

**北極星:** `docs/GWS_NORTH_STAR.md` — ワークスペース全体の GWS 二重アカウント。WBS-cloud 起動はゴールではない。

## ローカル完了判定

```bash
bash scripts/gws-verify-workspace.sh
```

## Cloud Agent で開いたら（任意リポ）

```bash
bash scripts/cloud-install.sh
bash scripts/verify-cloud-ready.sh
```

Cloud 起動は **API キー不要**。`cursor.com/agents` から UI 起動。Secrets は Dashboard 共通。

## Dashboard 前提（workspace 一度）

| Secret 名 | 用途 |
|-----------|------|
| `GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET` | 社内 / WBS |
| `GWS_CREDENTIALS_PICKLE_B64_PERSONAL` | 個人 |

登録: `bash scripts/prepare-dual-secrets.sh && python3 scripts/chrome-dashboard-setup.py`

## ルーティング

`docs/CURSOR_USER_RULE_GWS.md` / `.cursor/rules/gws-dual-account.mdc`

詳細: `docs/GWS_DUAL_ACCOUNT.md`, `docs/NEW_REPO_GWS.md`
