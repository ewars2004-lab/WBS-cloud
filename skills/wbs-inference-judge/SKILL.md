---
name: wbs-inference-judge
description: 完了候補の信頼度を判定し、LOWは完了禁止にする。
---

# WBS-Inference-Judge

Auditor 前のゲート。`Confidence.LOW` は state=完了 にしない。  
根拠リンクなし + MED は Tier B でブロック。
