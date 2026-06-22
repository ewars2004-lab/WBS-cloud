# Cloud Agent 完全セットアップ

WBS-cloud を Cloud Agent で **WBS 更新まで自律実行** するための手順。

## チェックリスト（全部 ✅ で運用開始）

### A. Cursor Dashboard（インフラ）

| # | 作業 | URL | 状態 |
|---|---|---|---|
| A1 | GitHub `ewars2004-lab` 接続 | https://cursor.com/dashboard?tab=integrations | 要確認 |
| A2 | Usage-based pricing ON | https://cursor.com/dashboard?tab=billing | 要確認 |
| A3 | **Slack MCP** OAuth | https://cursor.com/dashboard?tab=integrations → MCP → Slack → Connect | **要ログイン** |
| A4 | **Slack @Cursor** 連携 | https://cursor.com/dashboard?tab=integrations → Slack | **要ログイン** |
| A5 | Cloud Agent Secrets | https://cursor.com/dashboard/cloud-agents → Secrets | **要ログイン** |
| A6 | 環境に `ewars2004-lab/WBS-cloud` を登録 | https://cursor.com/dashboard/cloud-agents | 要確認 |

### B. Google Sheets（2段階: Secret 必須 + MCP 任意）

| 方式 | 必要な Dashboard 作業 | WBS 完遂 |
|---|---|---|
| **A. Secret のみ** | Cloud Agents → Secrets に `GWS_CREDENTIALS_PICKLE_B64` | ✅ CLI フォールバック（`scripts/sheets-cli.py`） |
| **B. Secret + MCP** | 上記 + Agents → MCP に `google-workspace-aircloset` 登録 | ✅ MCP ツールも利用可 |

Cloud Agent 検証（2026-06-22）では、リポジトリの `.cursor/mcp.json` だけでは **stdio MCP がカタログに載らない** 事象を確認。Slack（HTTP）は OK。

**最低限**: B-1 の Secret だけ設定すれば、`cloud-install.sh` が pickle を展開し Agent は CLI で Sheets 操作できる。

#### B-0. 完全自動（推奨・API キー1回だけ）

Dashboard への手動貼り付けを避ける場合:

```bash
cd ~/Projects/step-rope/WBS-cloud
./scripts/setup-cloud-complete.sh
# API キーを ~/.config/cursor/cloud-api-key に保存（Integrations → Cloud Agents API）
./scripts/launch-wbs-cloud-agent.sh launch
```

`launch` は API の `envVars` + `mcpServers` に認証を直渡しするため、**Secrets タブ・MCP タブへの貼り付けが不要**。

#### B-1. Secret を Dashboard に追加（Dashboard から手動起動する場合）

ローカル Mac で:

```bash
cd ~/Projects/step-rope/WBS-cloud
./scripts/setup-cloud-complete.sh
```

1. 開いた **Cloud Agents → Secrets** に `GWS_CREDENTIALS_PICKLE_B64` を貼る（スクリプトがクリップボードにコピー）
2. （任意）**Agents → MCP** に `google-workspace-aircloset` を貼る（同スクリプトが MCP ブロックもコピー）

手動で値だけ欲しい場合:

```bash
./scripts/prepare-secrets.sh
```

#### B-2. Dashboard で stdio MCP を追加（任意・ツール一覧に載せたい場合）

1. https://cursor.com/agents を開く
2. MCP 設定 → **Add MCP** または **Edit**
3. サーバー名: `google-workspace-aircloset`
4. `.local/dashboard-mcp-google-block.json` の内容を貼る（`env` に認証値入り。**共有しない**）

#### B-3. Secrets タブだけの場合

`GWS_CREDENTIALS_PICKLE_B64` を Secrets に入れると VM 全体の環境変数になる。`cloud-install.sh` が起動時に `~/.config/gws-aircloset/python-credentials.pickle` へ展開する。  
stdio MCP プロセスに env が渡らない場合でも **CLI フォールバックで完遂可能**。

### C. Slack ワークスペース側

- air-closet ワークスペースで MCP アプリが承認済みであること
- IP allowlist がある場合は Cursor を許可

### D. リポジトリ（本 PR で完了）

- [x] `skills/` — WBS更新チーム 5人格
- [x] `.cursor/mcp.json` — Slack + Sheets（stdio）
- [x] `.cursor/environment.json` — `cloud-install.sh`（Secrets → pickle）
- [x] `AGENTS.md` — Cloud Agent 入口 + CLI フォールバック
- [x] `scripts/sheets-cli.py` — Sheets MCP 未登録時の読み書き
- [x] `scripts/aircloset-sheets-mcp-cloud.py` — Secrets 対応 Sheets MCP

---

## OAuth 手順（Slack MCP）

1. https://cursor.com/dashboard を開く
2. **Integrations & MCP**（または Agents 画面の MCP ドロップダウン）
3. **Slack** を追加（`mcp.json` と同内容）または既存を確認
4. **Connect** → air-closet でログイン・承認

**Cloud Agent 用コールバック URL**（プロバイダ登録時）:

```
https://www.cursor.com/agents/mcp/oauth/callback
```

Desktop 用 `cursor://...` とは別。

---

## 初回検証プロンプト

https://cursor.com/agents で `ewars2004-lab/WBS-cloud` を選択し:

```
AGENTS.md と skills/wbs-update-workflow を読んでください。

1. 利用可能な MCP サーバーとツール一覧を表示
2. sheets_values_get で 新NagiWBS!A5:O5 を読む
3. Slack で 123067 after:2026-06-19 を検索
4. 結果を報告（MCP 状態・読取可否）
```

成功後:

```
WBS更新チームでバッチ実行。対象は進行中 or 完了根拠Slack空の行。
6/19以降の Slack を調査し、根拠がある行だけ新NagiWBSを更新してください。
```

---

## トラブルシュート

| 症状 | 対処 |
|---|---|
| Slack `needsAuth` | Dashboard で Slack MCP を Connect し直す |
| Sheets `credentials missing` | Secret `GWS_CREDENTIALS_PICKLE_B64` を Dashboard に追加 |
| OAuth scope null バグ | Desktop IDE で一度認証後、Dashboard でも再試行 |
| pj チャンネル検索 0 件 | 案件番号横断検索（`81205 after:...`）または `slack_read_channel` |

---

## 関連

- [mcp-setup.md](mcp-setup.md) — MCP 詳細
- [AUTOMATION.md](AUTOMATION.md) — 定期バッチ
- [NEW_PC_ONE_SHOT_PROMPT.md](../NEW_PC_ONE_SHOT_PROMPT.md) — Desktop 用
