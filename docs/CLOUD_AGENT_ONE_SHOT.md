# Cloud Agent ワンショット（WBS-cloud）

https://cursor.com/agents で本リポジトリを選び、以下を貼る。

---

あなたは **WBS更新チーム** の Cloud Agent です。`AGENTS.md` と `skills/wbs-update-workflow/SKILL.md` に従って実行してください。

## 前提確認（最初にやる）

1. MCP: Slack / google-workspace-aircloset が利用可能か
2. `sheets_values_get` で `新NagiWBS!A5:O5` が読めるか
3. Slack 検索が動くか（例: `123067 after:2026-06-19`）

いずれか失敗 → `docs/CLOUD_SETUP.md` の未完了項目を報告して **停止**。

## 本番タスク

```
対象期間: 先週金曜日（2026-06-19）00:00 JST 以降 〜 現在
```

1. **Planner** — 進行中 or H列空の行を抽出
2. **Slack調査** — 6/19以降の会話から状態を推察
3. **Writer** — 更新案作成（F列は air-closet 案件では触らない）
4. **Verifier** — 根拠と整合を確認
5. **Sheets 書き込み** — 承認行のみ `新NagiWBS` を更新
6. 曖昧行は Nagi DM に質問（WBSは触らない）
7. 完了報告（更新一覧・根拠リンク・要確認）

触ってよいのは **新NagiWBS のみ**。

---
