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
| `google-workspace-aircloset` | 新NagiWBS 読み書き |
| `figma` | 任意（WBS更新では通常不要） |

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

### 検証コマンド（起動直後）

1. `sheets_values_get` → `新NagiWBS!A5:O5`
2. Slack 検索 → `81205 after:YYYY-MM-DD`
3. 問題なければ Planner からバッチ開始

### セットアップ未完了時

`docs/CLOUD_SETUP.md` のチェックリストを確認。Secrets / OAuth が未設定なら作業を止めて報告する。
