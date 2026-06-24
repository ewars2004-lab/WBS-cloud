# GWS プラットフォーム — 北極星仕様

## 目的（これがゴール）

**Cursor ワークスペース全体**で、今後どの GitHub リポでも:

- GWS 二重アカウント（`aircloset` / `personal`）を
- **ローカル Cursor** と **Cloud Agents** の両方から使える

**Mac / ワークスペースで一度セットアップ。リポごとの OAuth・Secret 複製は原則なし。**

## 完了定義

| # | 条件 | 確認方法 |
|---|------|----------|
| L1 | aircloset OAuth 有効 | `gws-verify-profile.py aircloset` |
| L2 | personal OAuth 有効 | `gws-verify-profile.py personal` |
| L3 | グローバル MCP 有効 | `~/.cursor/mcp.json` + Cursor 再起動後にツール呼び出し |
| C1 | Dashboard Secrets 登録済み | Cloud Agents → Secrets に2名前 |
| C2 | 任意リポの Cloud Agent で GWS 動作 | VM 上で `verify-cloud-ready.sh` が OK |
| C2' | **ドライラン**（Agent 不要） | `bash scripts/gws-dry-run-cloud-verify.sh` |

**C2'** は Dashboard Secrets が VM に渡ったときと同じ経路を Mac で検証する。本番 C2 は Agent を **1本だけ** UI 起動。

**WBS-cloud の起動・API キー・WBS スプレッドシート読取は完了条件に含めない**（検証の一例にすぎない）。

## やらないこと（アンチパターン）

- Integrations ページで API キーを探す（存在しない）
- `launch-wbs-cloud-agent.sh` をゴールの必須経路にする（API キー不要なら UI 起動で足りる）
- WBS-cloud 専用 Cloud 起動だけを「目的達成」とみなす
- ユーザーに Dashboard コピペ・API キー手入力を常態化する（Tier3: 指紋・ログインのみ）

## 正しい経路

### ローカル（全リポ共通）

```bash
cd ~/Projects/WBS-cloud
bash scripts/gws-heal.sh --visual          # ローカルのみ
bash scripts/gws-verify-workspace.sh       # 完了判定
```

### Cloud（API キー不要）

1. Dashboard Secrets は workspace 共通（済なら触らない）
2. https://cursor.com/agents から任意リポで Agent 起動
3. プロンプト: `bash scripts/cloud-install.sh && bash scripts/verify-cloud-ready.sh`

自動化: `bash scripts/cloud-agent-ui-launch.sh`

### API 経路（任意・上級者のみ）

Mac から `curl api.cursor.com/v1/agents` で起動したい場合のみ `~/.config/cursor/cloud-api-key` が必要。  
**北極星の必須経路ではない。**

## WBS-cloud の位置づけ

- **スクリプト正本**（`scripts/gws-*`）の置き場
- **検証用リポの一例**（Sheets verify など）
- ゴールそのものではない

## エージェント向けチェック（毎タスク先頭）

作業開始前に自問:

1. これは「全リポ共通の GWS 基盤」か「特定リポの作業」か？
2. API キーは本当に必要か？（UI 起動 + Secrets で足りないか？）
3. ユーザーに手操作を求めているのは Tier3（指紋・ログイン）だけか？
