# GWS ワンショット自走

Dashboard を手で触らずに済ませる方法。

## 視覚モード（手順を見ながら進める）

`gws-bootstrap-all.sh` は内部で `--visual` を付けます。

- **Cursor | Chrome を画面分割**すると、ターミナルの `[手順]` / `👁` ログと Chrome の操作が対応します
- **普段の Chrome プロファイル**を使います（白画面になりやすい自動化用プロファイルは使いません）
- チャットにスクリーンショットは出しません（デバッグ時のみ `GWS_DEBUG=1`）

```bash
# ローカルだけ見ながら
bash scripts/gws-heal.sh --visual

# API キー + Cloud だけ再開
bash scripts/gws-resume-cloud.sh
```

Tier3（指紋・ログイン）だけ人間 → 完了後チャットで **「続けて」**。


```bash
cd ~/Projects/WBS-cloud
bash scripts/gws-bootstrap-all.sh
```

これだけで:

| 項目 | 方法 |
|------|------|
| ローカル MCP | `install-gws-mcp.sh` + `sync-cursor-mcp-json.py` |
| OAuth | pickle が無いときだけブラウザ（Google アカウント選択） |
| ルーティングルール | 各リポ `.cursor/rules/gws-dual-account.mdc`（Settings 貼り付け不要） |
| Cloud Secrets | **API 経路なら不要** / フォールバックは Chrome CDP 自動登録 |
| Cloud MCP Integrations | **API 経路なら不要**（payload に同梱） |
| Cloud Agent 起動 | `launch-wbs-cloud-agent.sh launch` |

## なぜ以前「手動」と言っていたか

Dashboard の **Integrations / Secrets を人間がブラウザで貼る**前提だったから。  
**Cloud Agents API** を使うと、起動 JSON の `envVars` + `mcpServers` に認証を直載せできるので Dashboard 登録をスキップできる。

## 唯一残りうる対話（初回のみ）

1. **Google OAuth** — pickle が無い Mac ではブラウザでアカウント選択（Google 側の制約）
2. **Cursor API キー** — `chrome-api-key-setup.py` が自動取得を試す。UI 変更で失敗したら1回だけ `pbpaste > ~/.config/cursor/cloud-api-key`

Secrets は既に登録済みなら触らなくてよい。API 起動なら Dashboard は二度と開かなくてよい。

## OAuth をやり直すとき

「将来」ではなく **同じコマンドを再実行**:

```bash
bash scripts/gws-oauth-login.sh aircloset   # または personal
bash scripts/prepare-dual-secrets.sh
bash scripts/gws-bootstrap-all.sh
```

## プラグイン / 依存

- **playwright** — Dashboard / API キーの Chrome CDP 自動化（`pip3 install playwright`）
- **Cloud Agents API** — 追加プラグイン不要。`~/.config/cursor/cloud-api-key` のみ
- **Cursor SDK** — 任意。同じ API を Python/TS から叩くなら `@cursor/sdk` / `cursor-sdk`

## 手動ルート（API を使わない場合）

```bash
bash scripts/setup-cloud-complete.sh   # JSON 生成 + ブラウザを開く
python3 scripts/chrome-dashboard-setup.py
```

API ルートの方が手数が少ない。
