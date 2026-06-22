# WBS-cloud

WBS 更新を Cursor **Cloud Agent** で実行するためのリポジトリ。

## セットアップ

Cloud Agent で Slack / Figma MCP を使う手順は [docs/mcp-setup.md](docs/mcp-setup.md) を参照。

リポジトリには [`.cursor/mcp.json`](.cursor/mcp.json) に HTTP MCP（Slack / Figma）の定義がある。  
**Dashboard での OAuth 認証は別途必要**（Desktop IDE の認証だけでは Cloud Agent では使えない）。

## WBS マスター

- Google スプレッドシート「新NagiWBS」  
  https://docs.google.com/spreadsheets/d/1VaQBMNy2ZCgYs57G2mQWiqof0sTH1umqY4HOjlZBLVE/edit?gid=2026060205
