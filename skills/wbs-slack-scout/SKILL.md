---
name: wbs-slack-scout
description: Nagi横断のメンション・DM・品質/MDチャンネルを横断検索する。
---

# WBS-Slack-Scout

`dict/channel_patterns.json` の `scout_channels` と  
`from:r.yaguchi` / `U08QC76DQRH` 検索で WBS未反映シグナルを拾い、  
Harvester と同形式で `state/inbox/scout_events.json` に保存。
