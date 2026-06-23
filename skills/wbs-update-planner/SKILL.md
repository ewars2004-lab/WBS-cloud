---
name: wbs-update-planner
description: WBS更新のPlanner。新NagiWBSから対象行（進行中 or 完了根拠Slack空）を切り出し、Slack調査ウィンドウを計算する。
---

# WBS更新 Planner

**新NagiWBS** を読み、バッチ対象行と Slack 調査範囲を決める。書き込みはしない。

## 正本

- リポジトリ: `~/Projects/step-rope/wbs-update-team/skills/wbs-update-planner/`
- Cursor: `~/.cursor/skills/wbs-update-planner/`

## 固定ID

- spreadsheet_id: `1VaQBMNy2ZCgYs57G2mQWiqof0sTH1umqY4HOjlZBLVE`
- シート名: `新NagiWBS`
- gid: `2026060205`

## 列定義（A〜O）

| 列 | ヘッダ | Plannerが使う |
|---|---|---|
| A | 案件 | 案件ID抽出 |
| B | 工程 | 工程名 |
| C | 見積もり工数 | 参照のみ |
| D | 次アクション / メモ | 次アクション |
| E | 状態 | **対象判定** |
| F | 完了期限 | **読取のみ・絶対編集禁止** |
| G | 完了日時 | 最終更新の参考 |
| H | 完了根拠Slackセリフリンク | **対象判定** |
| I | メモ | 既存メモ |
| J〜O | When〜How | 既存5W1H要約（お客様目線 — [5w1h-customer-view.md](../wbs-update-shared/5w1h-customer-view.md)） |

## 対象行の条件

```
対象 = (E列 == "進行中") OR (H列が空)
```

### MD系行の追加ルール

[md-calendar.md](../wbs-update-shared/md-calendar.md) を参照。

- MD系は Slack だけでなく **BSOMDスケジュールのカレンダー塗り** を調査対象に含める
- I列 / K列 から `年・シーズン・ブランド・担当` を抽出し `calendar_ref` として JSON に載せる
- `investigate_from` は通常どおり（最終更新 or 7日）。カレンダーは **現在の塗り状態** を読むので履歴深度とは別

- `完了` で H列にリンクがある行 → **スキップ**
- 案件指定モード時は A列でフィルタしたうえで上記を適用

## 調査ウィンドウ（Slack履歴）

各行について:

```
調査開始日 = min(今日 - 7日, 行の最終更新日)
```

**最終更新日** の決め方（優先順）:

1. G列（完了日時）があればその日付
2. なければ I列・D列のメモ内の最新日付っぽい記述
3. なければ今日 - 7日

Investigator へ `investigate_from`（ISO日付）を渡す。

## 手順

1. `sheets_values_get` で `新NagiWBS!A:O` を読む（大きい場合は E・H列で絞り込み後に行番号指定で再取得）
2. ヘッダ行（「案件」「工程」がある行）を特定
3. 対象行を抽出
4. 案件ID・工程・行番号・Where(K列)・現状態・調査開始日を JSON で出力

## 出力 JSON

```json
{
  "batch_id": "2026-06-19T10:20:00+09:00",
  "spreadsheet_id": "1VaQBMNy2ZCgYs57G2mQWiqof0sTH1umqY4HOjlZBLVE",
  "sheet_name": "新NagiWBS",
  "targets": [
    {
      "row": 12,
      "case_id": "AIRCLOSET-100031",
      "process": "開発進捗管理",
      "state": "進行中",
      "where": "#pj_120303",
      "evidence_slack": "https://...",
      "investigate_from": "2026-06-12",
      "memo_excerpt": "..."
    }
  ],
  "skipped_count": 45
}
```

## やってはいけないこと

- F列を書き換える提案
- 対象外の行を無理に含める
- 案件別シートの URL を更新対象に含める

## 参照

- 案件チャンネル: [case-channels.md](../wbs-update-shared/case-channels.md)
