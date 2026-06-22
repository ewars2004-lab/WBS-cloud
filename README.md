# WBS-cloud

**WBS更新チーム** を Cursor Cloud Agent で自律実行するリポジトリ。

## クイックスタート

### A. API 起動（Dashboard 貼り付け不要・推奨）

```bash
./scripts/setup-cloud-complete.sh
# Integrations → Cloud Agents API でキー作成 → 保存:
mkdir -p ~/.config/cursor && pbpaste > ~/.config/cursor/cloud-api-key && chmod 600 ~/.config/cursor/cloud-api-key
./scripts/launch-wbs-cloud-agent.sh launch
```

### B. Dashboard 手動起動

1. [docs/CLOUD_SETUP.md](docs/CLOUD_SETUP.md) のチェックリストを完了（Dashboard OAuth + Secrets）
2. https://cursor.com/agents で `ewars2004-lab/WBS-cloud` を起動
3. [docs/CLOUD_AGENT_ONE_SHOT.md](docs/CLOUD_AGENT_ONE_SHOT.md) のプロンプトを貼る

```bash
osascript scripts/open-dashboard-secrets.applescript  # Secret をクリップボード + Dashboard を開く
```

## 構成

```
WBS-cloud/
├── AGENTS.md                 ← Cloud Agent 入口
├── .cursor/
│   ├── mcp.json              ← Slack + Sheets + Figma
│   └── environment.json      ← pip install
├── skills/                   ← WBS更新チーム 5人格
├── docs/
│   ├── CLOUD_SETUP.md        ← セットアップチェックリスト
│   ├── CLOUD_AGENT_ONE_SHOT.md
│   ├── AUTOMATION.md         ← 定期バッチ
│   └── mcp-setup.md
└── scripts/
    ├── aircloset-sheets-mcp-cloud.py
    └── prepare-secrets.sh    ← ローカルで Secrets 値を生成
```

## 合言葉

- `WBS更新チームでバッチ実行`
- `先週金曜日以降の差分をWBSに反映して`

## WBS マスター

https://docs.google.com/spreadsheets/d/1VaQBMNy2ZCgYs57G2mQWiqof0sTH1umqY4HOjlZBLVE/edit?gid=2026060205

## Desktop IDE

```bash
./scripts/bootstrap.sh   # ~/.cursor/skills へ symlink（任意）
```

Cloud Agent はリポジトリ内 `skills/` を直接読むため bootstrap 不要。
