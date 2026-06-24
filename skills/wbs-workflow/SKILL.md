---
name: wbs-workflow
description: WBS更新チームのオーケストレータ。新NagiWBSをSlack実進捗とBSOMDカレンダーから自律更新する。17人格を指揮し、Auditor PASSまで回す。
---

# WBS更新チーム（オーケストレータ）

`新NagiWBS` を Slack + MDカレンダーから **抜け漏れなく推察更新** する。正本リポジトリ: `~/Projects/WBS-cloud`

## 起動トリガー

- `WBS更新チームで実行`
- `WBS更新`
- `新NagiWBSを更新`
- `WBS-cloud run`

## 実行前チェック

```bash
cd ~/Projects/WBS-cloud
./scripts/bootstrap.sh
python3 -m wbs_engine.runner doctor
python3 -m wbs_engine.runner validate
```

## チーム編成（この順で起動）

| 段 | Skill | 並列 |
|----|-------|------|
| 0 | [wbs-director](wbs-director/SKILL.md) | 1 |
| 1 | [wbs-cartographer](wbs-cartographer/SKILL.md) + [wbs-md-calendar-sync](wbs-md-calendar-sync/SKILL.md) | 2 |
| 2 | [wbs-channel-registry](wbs-channel-registry/SKILL.md) | 1 |
| 3 | [wbs-slack-harvester](wbs-slack-harvester/SKILL.md) ×3 + [wbs-slack-scout](wbs-slack-scout/SKILL.md) | 4 |
| 4 | [wbs-pj-analyst](wbs-pj-analyst/SKILL.md) ×4 + [wbs-cross-case-linker](wbs-cross-case-linker/SKILL.md) | 5 |
| 5 | [wbs-inference-judge](wbs-inference-judge/SKILL.md) | 1 |
| 6 | [wbs-delta-composer](wbs-delta-composer/SKILL.md) + [wbs-5w1h-writer](wbs-5w1h-writer/SKILL.md) | 2 |
| 7 | [wbs-auditor](wbs-auditor/SKILL.md) → [wbs-sheet-writer](wbs-sheet-writer/SKILL.md) | 順次 |
| 8 | [wbs-run-reporter](wbs-run-reporter/SKILL.md) | 1 |

## 完了条件

1. **wbs-auditor** が Tier C = 0
2. **wbs-sheet-writer** が書込完了（または dry-run 承認）
3. **wbs-run-reporter** が変更サマリ出力

Tier C が1件でもあれば **Writer 停止** → Analyst へ差し戻し。

## 最重要ルール（全員共通）

- **F列**: AIRCLOSET案件は絶対編集禁止。MDブランド行（`ブランド：シーズン`）のみ更新可
- 既存行の削除・並べ替え禁止。追記と限定列更新のみ
- E列は `完了` / `未着手` / `進行中` のみ
- 完了には H列 Slack個別発言リンク必須（LOW信頼度は完了禁止）
- 完了済み作成/修正行は未完了に戻さない。FBは新規修正行へ積む

## 参照

- WBS: https://docs.google.com/spreadsheets/d/1VaQBMNy2ZCgYs57G2mQWiqof0sTH1umqY4HOjlZBLVE/edit?gid=2026060205
- MD: https://docs.google.com/spreadsheets/d/1x9urTyDl_obuvbTCJVj3FlpYNFljRZNS6XdZcMOw2TQ/edit?gid=394259552
- 詳細指示: スプレッドシート `Claude_新NagiWBS指示` タブ

## 1 Run の出力テンプレ

```markdown
## WBS更新チーム — Run {id}

- 更新行: ...
- 追加行: ...
- MD同期: N件
- 見送り（曖昧）: ...
- Auditor: PASS / FAIL
```
