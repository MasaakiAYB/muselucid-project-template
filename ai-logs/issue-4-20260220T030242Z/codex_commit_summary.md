Codex-Context:
- 指示:
  - Issue: #4 READMEと検証手順を整備する
  - Issue本文の要点: Plan-ID: ISSUE-0003
  - Plannerへ渡した方針: あなたは Planner エージェントです。
  - Issue要求: Plan-ID: ISSUE-0003
- 試行錯誤:
  - attempt 1 [passed]: 目的=あなたは Coder エージェントです。 / 実施=README を Issue #4 のスコープに合わせて更新し、実装と整合する検証手順を追加しました。 / 結果=PASS `git diff --check`
- 設計根拠:
  - 採用設計: スコープ（対象/対象外）
  - 設計根拠(Issue): Plan-ID: ISSUE-0003
  - 設計根拠(Planner): あなたは Planner エージェントです。
  - 設計根拠(Plan): **対象**
  - 検証方針: `git diff --check`

Codex-Log-Reference:
- AI Logs: ai-logs/issue-4-20260220T030242Z/index.md
