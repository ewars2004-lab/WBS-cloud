#!/usr/bin/env osascript
-- WBS-cloud: Secret をクリップボードに入れ Dashboard を開く
set repoRoot to POSIX path of (path to home folder as text) & "Projects/step-rope/WBS-cloud/"
set secretPath to repoRoot & ".local/GWS_CREDENTIALS_PICKLE_B64.txt"

try
  set secretText to read POSIX file secretPath as «class utf8»
  set the clipboard to secretText
on error
  display dialog "先に WBS-cloud で ./scripts/setup-cloud-complete.sh を実行してください。" buttons {"OK"} default button 1 with title "WBS-cloud"
  return
end try

open location "https://cursor.com/dashboard/cloud-agents"
delay 1
open location "https://cursor.com/agents"

display notification "Secrets → Add → Name: GWS_CREDENTIALS_PICKLE_B64 → Cmd+V" with title "WBS-cloud" subtitle "クリップボードに Secret 値をコピー済み"
