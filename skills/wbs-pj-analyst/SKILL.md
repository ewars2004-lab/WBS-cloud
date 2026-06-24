---
name: wbs-pj-analyst
description: 案件単位でSlackイベントをWBS工程にマッピングする。
---

# WBS-PJ-Analyst

`wbs_engine.inference` のルールに従い:

- HIGH: 修正しました、対応完了、リリースしました → 完了候補
- MED: Figma/総合テスト/STG → 進行中
- LOW: 確認します、いけそう → 見送り

後工程到達で前工程完了扱い可（D/Iに根拠必須）。
