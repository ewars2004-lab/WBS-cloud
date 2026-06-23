---
name: wbs-update-workflow
description: WBS更新チームのオーケストレータ。新NagiWBSをSlack会話から推察して更新。定期バッチ（平日10:20・19:00）とDM返答トリガーを管理する。
---

# WBS更新チーム（オーケストレータ）

**新NagiWBS** を Slack の会話から推察して自動更新する。5人格を順に回す。

## 人格と Skill

| 順 | 人格 | Skill |
|---|---|---|
| 1 | Planner | [wbs-update-planner](../wbs-update-planner/SKILL.md) |
| 2 | Slack調査 | [wbs-slack-investigator](../wbs-slack-investigator/SKILL.md) |
| 3 | WBS更新 | [wbs-update-writer](../wbs-update-writer/SKILL.md) |
| 4 | Verifier | [wbs-update-verifier](../wbs-update-verifier/SKILL.md) |

## 起動モード

| モード | きっかけ | やること |
|---|---|---|
| **定期バッチ** | 平日 10:20 / 19:00、または `WBS更新チームでバッチ実行` | 全対象行を処理 → Nagi DM にサマリー |
| **案件指定** | `WBS更新チーム、81205を調査して` | 該当案件の対象行のみ |
| **DM返答** | Nagi が曖昧質問に返答 | 該当1行だけ即時反映 |

## ループ手順

```
[開始]
   ↓
① Planner — 対象行リスト + 調査ウィンドウ
   ↓
② Slack調査 — 行ごとに推察パケット
   ↓
   曖昧? ──Yes──→ Nagi DM（スレッドリンク＋質問）→ その行スキップ
   ↓ No
③ WBS更新 — 更新案（JSON）
   ↓
④ Verifier — 反映可 / 差し戻し / 曖昧
   ↓
 差し戻し? ──Yes──→ ② or ③ へ（最大3ラウンド）
   ↓ 反映可
 Sheets 書き込み
   ↓
[次の行 or バッチ完了 → Nagi DM サマリー]
```

### ループ上限

- 1行あたり最大 **3ラウンド**。超えたらその行はスキップし Nagi DM にエスカレーション。

## 絶対ルール

- **触ってよいのは `新NagiWBS` のみ**
- **F列（完了期限）**: air-closet 案件は編集しない。**MD系のみ** [md-calendar.md](../wbs-update-shared/md-calendar.md) のカレンダー塗りから反映可
- 案件別スプレッドシート（5W1Hタブ・総合テスト・Figma）は触らない
- 既存行・列・メモ・リンクを **削除しない**（追記・上書きは更新対象列のみ）
- E列の状態は **完了 / 未着手 / 進行中** のみ
- 完了済みの作成行を未完了に戻さない（Shuri人格チームと同じ原則）

## Nagi DM

### 曖昧時（調査中）

```
【WBS更新チーム】状態の確認

案件: {案件ID}
工程: {工程名}
スレッド: {Slack permalink}

会話を追いましたが、状態の判断がつきませんでした。
これはどういう状態ですか？

（例: 進行中 / 完了 / 未着手、または短い補足）
```

### バッチ完了サマリー

```
WBS更新チーム — バッチ完了（{日時} JST）

更新: {n}件
曖昧（要回答）: {n}件
スキップ: {n}件
エラー: {n}件

【更新した案件】
- {案件} / {工程} → {状態}

【要回答】
- {案件} / {工程} → {permalink}
```

送信先: **Nagi の自分 DM**（他メンバーに見えない場所）。

## 1ラウンドの出力テンプレ

```markdown
## WBS更新チーム — {モード} — {日時}

**対象**: {n}行
**状態**: 進行中

### ① Planner
- 対象行: ...

### ② Slack調査
- 推察完了: {n}行 / 曖昧: {n}行

### ③ WBS更新
- 更新案: {n}件

### ④ Verifier
- 反映: {n}件 / 差し戻し: {n}件

### 次アクション
- {続行 / Nagi DM / 完了}
```

## 参照

- WBS: https://docs.google.com/spreadsheets/d/1VaQBMNy2ZCgYs57G2mQWiqof0sTH1umqY4HOjlZBLVE/edit?gid=2026060205
- spreadsheet_id: `1VaQBMNy2ZCgYs57G2mQWiqof0sTH1umqY4HOjlZBLVE`
- シート名: `新NagiWBS`
- 案件チャンネル: [case-channels.md](../wbs-update-shared/case-channels.md)
- 5W1Hお客様目線: [5w1h-customer-view.md](../wbs-update-shared/5w1h-customer-view.md)
- Automation: [docs/AUTOMATION.md](../../docs/AUTOMATION.md)
