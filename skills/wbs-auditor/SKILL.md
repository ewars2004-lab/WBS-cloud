---
name: wbs-auditor
description: F列保護・根拠必須・状態値検証。Tier CでWriter停止。
---

# WBS-Auditor

`wbs_engine.auditor.audit_patches` が正本。

Tier C（即停止）:
- F_FORBIDDEN: 非MD行のF列変更
- INVALID_STATE / DELETE_ROW

Tier B:
- MISSING_EVIDENCE: 完了なのにH列なし
