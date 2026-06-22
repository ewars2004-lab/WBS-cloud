# Cloud Agent MCP セットアップ

Cursor **Cloud Agent**（https://cursor.com/agents）から Slack / Figma の MCP ツールを使うための手順。

**重要**: Desktop IDE で MCP を認証済みでも、Cloud Agent では **別途 OAuth** が必要。

---

## 前提（Phase 0）

| 項目 | 確認方法 | 備考 |
|---|---|---|
| Cursor 有料プラン | Dashboard → Billing | Pro / Teams 等 |
| GitHub `ewars2004-lab` 権限 | リポジトリ Settings → Collaborators | WBS-cloud の read/write |
| Slack ワークスペース | air-closet.slack.com | MCP 承認が必要な場合あり |
| Figma アカウント | figma.com | Figma MCP を使う場合 |

---

## 2種類の Slack 連携（混同しない）

| 種類 | 用途 | 設定場所 |
|---|---|---|
| **Slack 連携（@Cursor）** | Slack から Cloud Agent を起動 | Dashboard → Integrations → Slack |
| **Slack MCP** | Agent がメッセージ検索・読取・送信 | Dashboard → Integrations & MCP / Agents の MCP |

WBS 更新には **両方** 必要。@Cursor だけではチャンネル内の会話は読めない。

---

## リポジトリ側の設定

本リポジトリの [`.cursor/mcp.json`](../.cursor/mcp.json):

```json
{
  "mcpServers": {
    "slack": {
      "url": "https://mcp.slack.com/mcp",
      "auth": {
        "CLIENT_ID": "3660753192626.8903469228982"
      }
    },
    "figma": {
      "url": "https://mcp.figma.com/mcp"
    }
  }
}
```

Cloud Agent は **HTTP MCP** を推奨（stdio は VM 内でトークンが露出しうる）。

---

## Phase 1: Cloud Agent 基盤

1. https://cursor.com/dashboard を開く
2. **GitHub** で `ewars2004-lab` を接続
3. **Usage-based pricing** を有効化（Cloud Agent 利用に必要）
4. **Privacy** 設定を確認

### Slack 連携（@Cursor 起動用）

1. Dashboard → **Integrations** → **Slack** → **Connect**
2. air-closet ワークスペースに Cursor アプリをインストール
3. 任意チャンネルで `@Cursor help` → 応答があれば OK

---

## Phase 2: Slack MCP

### Dashboard で追加

1. Dashboard → **Integrations & MCP**（または https://cursor.com/agents の MCP ドロップダウン）
2. 上記 `mcp.json` と同等の Slack サーバーを追加
3. 行の **Connect / Sign in** で OAuth

**Cloud Agent 用 OAuth コールバック URL**（プロバイダ登録時）:

```
https://www.cursor.com/agents/mcp/oauth/callback
```

Desktop IDE 用 `cursor://anysphere.cursor-mcp/oauth/callback` とは別。混同しないこと。

### Slack ワークスペース側

- [Slack MCP 公式ドキュメント](https://docs.slack.dev/ai/mcp-server/)
- MCP 連携がワークスペース管理者により承認済みであること
- アプリが Directory-published または Internal（Unlisted は MCP 不可）
- IP allowlist がある場合は Cursor の IP を許可

---

## Phase 3: Figma MCP（任意）

1. Dashboard の MCP に `https://mcp.figma.com/mcp` を追加
2. **Connect** → Figma アカウントで承認
3. Figma 側リダイレクト URI に `https://www.cursor.com/agents/mcp/oauth/callback` を登録

WBS マスターは Google スプレッドシート（新NagiWBS）のため、Figma MCP は案件 Figma 確認用。

---

## Phase 4: 動作検証

### 4-1. Cloud Agent で MCP 状態確認

https://cursor.com/agents から本リポジトリ `ewars2004-lab/WBS-cloud` で Agent を起動し、例:

```
利用可能な MCP サーバーとツールの一覧を表示してください。
Slack MCP の serverStatus が needsAuth でないこと、
利用可能なツールが 1 件以上あることを確認してください。
```

| チェック | 期待 |
|---|---|
| Slack MCP serverStatus | `needsAuth` ではない |
| Slack MCP ツール数 | 1 件以上（search / read channel 等） |
| Figma MCP serverStatus | `error` ではない（設定時） |

### 4-2. Slack 実動作テスト

```
「WBS」または「更新」を含むチャンネルを検索し、
直近 3 日分のメッセージを取得してください。
```

### 4-3. ローカル IDE での参考検証（2026-06-22）

Desktop IDE（Cursor プラグイン `plugin-slack-slack`）では以下を確認済み:

- `slack_search_channels` / `slack_search_public_and_private` が応答
- `#pj_123067_発注配送登録連絡のシステム化` の 6/22 メッセージ取得
- 案件 ID 横断検索（例: `69776 after:2026-06-19`）が可能

Cloud Agent 側は Dashboard OAuth 完了後に同様のテストを実施すること。

---

## WBS 更新に必要な追加 MCP（Google Sheets）

WBS 本体の読み書きには **新NagiWBS** スプレッドシートが必要:

- spreadsheetId: `1VaQBMNy2ZCgYs57G2mQWiqof0sTH1umqY4HOjlZBLVE`
- シート名: `新NagiWBS`

Desktop IDE では stdio の `google-workspace-aircloset`（aircloset-sheets-mcp）を使用。  
**Cloud Agent では stdio MCP は非推奨**のため、Sheets 書き込み方法は別途検討が必要（HTTP 化・Secrets 注入・手動反映など）。

詳細: [step-rope/shuri-team/docs/MCP_SETUP.md](https://github.com/ewars2004-lab/shuri-team/blob/main/docs/MCP_SETUP.md)（社内リポジトリ）

---

## 既知の制限・トラブルシューティング

### Cloud Agent と Desktop の認証は別

Desktop で Slack MCP が動いても Cloud Agent は Dashboard / Agents 画面から再認証。

### OAuth scope の既知バグ

Cloud Agent が OAuth 時に `scope: null` を送る既知問題あり。  
失敗時は Desktop IDE 経由の認証を試す。  
参考: https://forum.cursor.com/t/cursor-cloud-agents-bug-in-oauth-scope-handling/160396

### Slack MCP が `needsAuth` のまま

1. Dashboard → MCP → Slack → Connect を再実行
2. Slack 管理者に MCP アプリ承認を依頼
3. 別ブラウザ / シークレットウィンドウで OAuth 再試行

### Figma MCP が `error`

1. `https://mcp.figma.com/mcp` の URL  typo 確認
2. Figma OAuth リダイレクト URI に Cloud Agent コールバックを登録
3. Dashboard で Disconnect → 再 Connect

### Slack 検索が 0 件

- `in:#pj_XXXXX` より案件番号横断検索（例: `81205 after:YYYY-MM-DD`）を試す
- `slack_read_channel` で channel_id 直接読取

### Slack MCP レート制限

- search: 特別制限あり
- read channel: Tier 3（50+/分）

---

## 検証ログ

| 日時 (JST) | 環境 | Slack | Figma | 備考 |
|---|---|---|---|---|
| 2026-06-22 | Desktop IDE (plugin-slack-slack) | ✅ 検索・読取可 | 未検証 | Cloud Agent OAuth は未実施（Dashboard 操作要） |
| （記入） | Cloud Agent | | | Dashboard OAuth 後に更新 |

---

## 関連リンク

- WBS マスター: https://docs.google.com/spreadsheets/d/1VaQBMNy2ZCgYs57G2mQWiqof0sTH1umqY4HOjlZBLVE/edit?gid=2026060205
- Cursor Agents: https://cursor.com/agents
- Cursor Dashboard: https://cursor.com/dashboard
- Slack MCP: https://docs.slack.dev/ai/mcp-server/
