# MCP / 認証セットアップ（どのPCでも共通）

## 1. Google Workspace（必須）

**デュアルアカウント（全リポジトリ共通・正本）**: [docs/GWS_DUAL_ACCOUNT.md](docs/GWS_DUAL_ACCOUNT.md)

```bash
bash scripts/install-gws-mcp.sh
bash scripts/gws-oauth-login.sh aircloset
bash scripts/gws-oauth-login.sh personal
```

Cloud Agent: [AGENTS.md](AGENTS.md) / `bash scripts/setup-cloud-complete.sh`

### 依存パッケージ

```bash
pip install -r requirements.txt
```

## 2. Slack（任意・推奨）

### 方法A: Cursor Slack MCP（推奨）

1. 案件チャンネル `pj_*` を上から下まで読む（スレッド含む）
2. Nagi / r.yaguchi / U08QC76DQRH のメンション・DMも検索
3. 結果を `state/inbox/slack_events.json` に保存:

```json
[
  {
    "channel_name": "#pj_60434_xxx",
    "message_ts": "1780968935.000000",
    "permalink": "https://air-closet.slack.com/archives/...",
    "text": "AIRCLOSET-60434 修正しました",
    "user": "Nagi"
  }
]
```

### 方法B: Slack Bot Token

```bash
export SLACK_BOT_TOKEN="xoxb-..."
```

`search.messages` スコープが必要です。

## 3. 動作確認

```bash
./scripts/wbs-run.sh doctor    # 認証・スキルリンク確認
./scripts/wbs-run.sh validate  # ユニットテスト
./scripts/wbs-run.sh run       # dry-run
```

## 4. 定期実行（任意）

平日 10:05 / 19:00 JST:

```cron
5 10 * * 1-5 cd ~/Projects/WBS-cloud && ./scripts/wbs-run.sh run --apply >> state/cron.log 2>&1
0 19 * * 1-5 cd ~/Projects/WBS-cloud && ./scripts/wbs-run.sh run --apply >> state/cron.log 2>&1
```

## 5. トラブルシュート

| 症状 | 対処 |
|------|------|
| `gws_credentials: false` | pickle パスを確認 |
| Slack更新されない | `state/inbox/*.json` を投入するか SLACK_BOT_TOKEN を設定 |
| MD F列が更新されない | BSOMDの塗り色が `dict/color_semantics.json` と一致するか確認 |
| Auditor FAIL | `state/run_*.md` の見送り理由を確認 |
