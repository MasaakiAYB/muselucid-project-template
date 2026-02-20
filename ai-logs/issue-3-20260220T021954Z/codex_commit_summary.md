Codex-Context:
- 指示:
  - Issue: #3 取得したヘッドラインをCLIで表示する
  - Issue本文の要点: Plan-ID: ISSUE-0002
  - Plannerへ渡した方針: あなたは Planner エージェントです。
  - Issue要求: Plan-ID: ISSUE-0002
- 試行錯誤:
  - attempt 1 [passed]: 目的=あなたは Coder エージェントです。 / 実施=実装完了しました。Issue #3 のスコープに合わせて、最新ヘッドライン表示CLIを追加しています。 / 結果=PASS `git diff --check`
- 設計根拠:
  - 採用設計: スコープ（対象/対象外）
  - 設計根拠(Issue): Plan-ID: ISSUE-0002
  - 設計根拠(Planner): あなたは Planner エージェントです。
  - 設計根拠(Plan): **対象（In Scope）**
  - 検証方針: `git diff --check`

Codex-Log-Reference:
- AI Logs: ai-logs/issue-3-20260220T021954Z/index.md
