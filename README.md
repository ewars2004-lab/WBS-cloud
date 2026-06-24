# WBS-cloud — 新NagiWBS 自動更新チーム

Slack実進捗と BSOMDカレンダー（塗りセル）から `新NagiWBS` を自律更新するエンジンです。  
**どのPCでも** 同じ手順でセットアップできます。

## クイックスタート（任意のPC）

```bash
git clone https://github.com/ewars2004-lab/WBS-cloud.git ~/Projects/WBS-cloud
cd ~/Projects/WBS-cloud
chmod +x scripts/*.sh
./scripts/bootstrap.sh
```

Google認証を設定したあと:

```bash
source .venv/bin/activate
./scripts/wbs-run.sh doctor
./scripts/wbs-run.sh validate
./scripts/wbs-run.sh run              # dry-run（書込なし）
./scripts/wbs-run.sh run --apply      # 本番書込
```

## Cursor から使う

1. `bootstrap.sh` で `wbs-workflow` スキルを `~/.cursor/skills/` にリンク
2. チャットで **「WBS更新チームで実行」** と依頼
3. エージェントは Slack MCP で `state/inbox/*.json` にイベントを保存 → `wbs-run run` を実行

## アーキテクチャ

| モジュール | 役割 |
|-----------|------|
| `cartographer` | WBS行の解析・案件インデックス |
| `md_calendar` | BSOMD塗りセル → MDブランド行F列 |
| `slack_events` | inbox JSON / Slack API からイベント収集 |
| `inference` | Slack → 完了/進行中の推察 |
| `auditor` | F列保護・根拠必須・Tier判定 |
| `orchestrator` | 全工程を1 Run に統合 |
| `sheet_writer` | Google Sheets へバッチ書込 |

## 最重要ルール

- **F列**: AIRCLOSET案件は編集禁止。`ブランド：シーズン` のMD行のみ更新可
- 既存行の削除・並べ替え禁止
- E列は `完了` / `未着手` / `進行中` のみ
- 完了には H列 Slackリンク必須（LOW信頼度は完了禁止）

## 対象シート

- WBS: [新NagiWBS](https://docs.google.com/spreadsheets/d/1VaQBMNy2ZCgYs57G2mQWiqof0sTH1umqY4HOjlZBLVE/edit?gid=2026060205)
- MD: [BSOMDスケジュール](https://docs.google.com/spreadsheets/d/1x9urTyDl_obuvbTCJVj3FlpYNFljRZNS6XdZcMOw2TQ/edit?gid=394259552)

詳細は [MCP_SETUP.md](MCP_SETUP.md) と `skills/wbs-workflow/SKILL.md` を参照。
