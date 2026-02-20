レビューを実施し、品質レポートを以下に作成しました。

- `/home/runner/work/FlowSmith/FlowSmith/.agent/runs/masaakiayb-muselucid-project-template/20260220T022401Z-issue-3/review.md`

主な指摘は2点です。
1. `--raw unexpected` のような余剰引数が無視される（usageエラー検知不足）。
2. ISSUE-0001の取得処理との接続要件がコード上で確認できず、取得ロジック重複リスクがある。