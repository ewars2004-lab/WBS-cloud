# 別 PC ワンショット（WBS更新チーム）

Cursor Agent に以下を全文貼る。

---

あなたは WBS更新チーム の新 PC セットアップ担当です。順番に実行し、完了報告してください。

## 定数

- REMOTE_URL: （未作成ならローカルのみ）`~/Projects/step-rope/wbs-update-team`
- CLONE_DIR: `~/Projects/step-rope/wbs-update-team`
- WBS: https://docs.google.com/spreadsheets/d/1VaQBMNy2ZCgYs57G2mQWiqof0sTH1umqY4HOjlZBLVE/edit?gid=2026060205

## 手順

### 1. リポジトリ

`git clone` または既存ディレクトリで `cd ~/Projects/step-rope/wbs-update-team`

### 2. bootstrap

```bash
chmod +x scripts/bootstrap.sh
./scripts/bootstrap.sh
```

`~/.cursor/skills/wbs-update-workflow` ほか5つが symlink になっていること。

### 3. MCP

`docs/MCP_SETUP.md` に従い:

- google-workspace-aircloset（新NagiWBS）
- plugin-slack-slack（案件チャンネル + Nagi DM）

`sheets_values_get` で `新NagiWBS!A5:O5` が読めること。

### 4. Automation（任意）

`docs/AUTOMATION.md` で平日 10:20 / 19:00 JST の定期バッチを設定。

## 完了報告

- bootstrap: OK/NG
- MCP sheets: OK/NG
- MCP slack: OK/NG

## 合言葉

- `WBS更新チームでバッチ実行`
- `WBS更新チーム、100031を調査して`
- `WBS更新チーム 応答せよ`

---
