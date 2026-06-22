# WBS-cloud — Cloud Agent 入口

このリポジトリは **WBS更新チーム** を Cursor Cloud Agent で自律実行するための正本です。

## 合言葉

- `WBS更新チームでバッチ実行`
- `WBS更新チーム、81205を調査して`
- `先週金曜日以降の差分をWBSに反映して`

## Cursor Cloud specific instructions

### 起動時に読む Skills（リポジトリ内）

1. `skills/wbs-update-workflow/SKILL.md`
2. `skills/wbs-update-planner/SKILL.md`
3. `skills/wbs-slack-investigator/SKILL.md`
4. `skills/wbs-update-writer/SKILL.md`
5. `skills/wbs-update-verifier/SKILL.md`

共有参照:

- `skills/wbs-update-shared/case-channels.md`
- `skills/wbs-update-shared/md-calendar.md`

### MCP（`.cursor/mcp.json`）

| MCP | 用途 |
|---|---|
| `slack` | 案件チャンネル調査・Nagi DM |
| `google-workspace-aircloset` | 新NagiWBS 読み書き（Dashboard 登録が必要な場合あり） |

### Google Sheets — MCP が使えないときのフォールバック

VM の Secret `GWS_CREDENTIALS_PICKLE_B64` が設定されていれば、`scripts/cloud-install.sh` が起動時に認証を展開する。  
**stdio MCP がカタログに無くても** 次の CLI で読み書きできる（WBS 更新は継続すること）:

```bash
# ヘッダ行の読取（検証）
python3 scripts/sheets-cli.py verify

# 任意レンジ
python3 scripts/sheets-cli.py values-get \
  --spreadsheet 1VaQBMNy2ZCgYs57G2mQWiqof0sTH1umqY4HOjlZBLVE \
  --range '新NagiWBS!A5:O5'

# 更新（values は 2D JSON 配列の文字列）
python3 scripts/sheets-cli.py values-update \
  --spreadsheet 1VaQBMNy2ZCgYs57G2mQWiqof0sTH1umqY4HOjlZBLVE \
  --range '新NagiWBS!E171' \
  --values '[["進行中"]]'
```

MCP ツール名との対応: `sheets_values_get` → `values-get`、`sheets_values_update` → `values-update`。

### 絶対ルール

- **触ってよいのはスプレッドシート `新NagiWBS` のみ**
- **F列（完了期限）**: air-closet 案件は編集禁止。MD系のみカレンダー塗りから可
- 案件別スプレッドシート（5W1H・総合テスト・Figma）は触らない
- E列は `完了` / `未着手` / `進行中` のみ
- 完了済み行を未完了に戻さない
- 曖昧な行は WBS を触らず Nagi DM に質問

### WBS 正本

- spreadsheet_id: `1VaQBMNy2ZCgYs57G2mQWiqof0sTH1umqY4HOjlZBLVE`
- シート名: `新NagiWBS`
- URL: https://docs.google.com/spreadsheets/d/1VaQBMNy2ZCgYs57G2mQWiqof0sTH1umqY4HOjlZBLVE/edit?gid=2026060205

### 定期バッチ

`docs/AUTOMATION.md` 参照。平日 10:20 / 19:00 JST。

### 検証（起動直後）

1. Slack: 検索 `81205 after:YYYY-MM-DD` が返ること
2. Sheets: `sheets_values_get` または `python3 scripts/sheets-cli.py verify`
3. 問題なければ Planner からバッチ開始

### セットアップ未完了時

`docs/CLOUD_SETUP.md` のチェックリストを確認。

- Slack `needsAuth` → Dashboard で Connect
- Sheets 認証なし → Secret `GWS_CREDENTIALS_PICKLE_B64` を Dashboard に追加（ローカルで `./scripts/setup-cloud-complete.sh`）
