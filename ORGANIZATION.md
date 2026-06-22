# ステップロープ社 — WBS更新チーム

Slack のやり取りを会話として読み、**新NagiWBS** の進捗行を自動更新する Cursor エージェントチーム。

## メンバー（5人格）

| 順 | 人格 | Skill | やること |
|---|---|---|---|
| 1 | オーケストレータ | `wbs-update-workflow` | バッチ/DM返答の起動、ループ管理、Nagiへ報告 |
| 2 | Planner | `wbs-update-planner` | 対象行の切り出し、調査ウィンドウの計算 |
| 3 | Slack調査 | `wbs-slack-investigator` | チャンネル・横断検索、会話から状態推察 |
| 4 | WBS更新 | `wbs-update-writer` | 新NagiWBS への書き込み案作成 |
| 5 | Verifier | `wbs-update-verifier` | 根拠と推察の整合確認 → OKなら反映 |

## 正本の場所

```
~/Projects/step-rope/wbs-update-team/
```

Cursor は `scripts/bootstrap.sh` で `~/.cursor/skills/wbs-*` に symlink する。

## 起動パターン

| パターン | タイミング | トリガー例 |
|---|---|---|
| 定期バッチ | 平日 10:20・19:00 JST | Cursor Automation / 手動「バッチ実行」 |
| DM返答 | Nagiが曖昧質問に返答した直後 | Automation（Slack DM）または手動 |

## 完了条件（バッチ1行あたり）

1. Verifier が **反映可** と判定
2. Writer が Sheets MCP で書き込み完了
3. 曖昧な行は WBS を触らず Nagi DM に質問

## Shuri人格チームとの関係

| | WBS更新チーム | Shuri人格チーム |
|---|---|---|
| 触る場所 | **新NagiWBS のみ** | 案件別シート（5W1Hタブ・総合テスト・Figma） |
| 目的 | 進捗・根拠・要約の同期 | 提出物品質（ティアA） |

**衝突しない。** 別ファイル・別目的。

## 参照

- WBS: https://docs.google.com/spreadsheets/d/1VaQBMNy2ZCgYs57G2mQWiqof0sTH1umqY4HOjlZBLVE/edit?gid=2026060205
- 案件チャンネル: `skills/wbs-update-shared/case-channels.md`
- MD期日（カレンダー塗り）: `skills/wbs-update-shared/md-calendar.md`
