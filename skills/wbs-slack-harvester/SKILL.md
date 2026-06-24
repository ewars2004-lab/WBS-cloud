---
name: wbs-slack-harvester
description: 案件チャンネルpj_*を上から下まで読み、state/inboxにJSON保存する。
---

# WBS-Slack-Harvester

Cursor Slack MCP で以下を実施:

1. WBS上の各 `AIRCLOSET-*` から `pj_{id}_` チャンネルを特定
2. `slack_read_channel` でページング（スレッドは `slack_read_thread`）
3. `state/inbox/slack_events.json` に配列で保存

必須フィールド: `channel_name`, `message_ts`, `permalink`, `text`
