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

### B. Cursor Secrets（Google Sheets 用）

Dashboard → **Cloud Agents** → **Secrets** に以下を追加:

| Secret 名 | 値の作り方 |
|---|---|
| `GWS_CREDENTIALS_PICKLE_B64` | ローカル Mac で `./scripts/prepare-secrets.sh` を実行し、出力をコピペ |

（任意）`GWS_CLIENT_SECRET_JSON` — OAuth 再認証が必要な場合のみ。通常は pickle のみで可。

### C. Slack ワークスペース側

- air-closet ワークスペースで MCP アプリが承認済みであること
- IP allowlist がある場合は Cursor を許可

### D. リポジトリ（本 PR で完了）

- [x] `skills/` — WBS更新チーム 5人格
- [x] `.cursor/mcp.json` — Slack + Sheets + Figma
- [x] `.cursor/environment.json` — pip install
- [x] `AGENTS.md` — Cloud Agent 入口
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
