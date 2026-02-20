実装完了しました。Issue #3 のスコープに合わせて、最新ヘッドライン表示CLIを追加しています。

**変更内容**
- `scripts/show_latest_headline.sh` を新規作成
- 処理を関数分離
  - `fetch_latest_headline_raw`（取得）
  - `format_headline`（整形）
  - `print_headline`（出力）
  - `main`（`取得 -> 整形 -> 出力`）
- 異常系で `stderr` に明確なメッセージを出し、非0終了
- 依存要件（ISSUE-0001接続）として `--raw` / `--source-check` も実装

**実行確認**
- `./scripts/show_latest_headline.sh` 成功（1件表示、終了コード0）
- `./scripts/show_latest_headline.sh >/tmp/headline.out && test -s /tmp/headline.out` 成功
- `./scripts/show_latest_headline.sh 2>/tmp/headline.err || test -s /tmp/headline.err` 成功
- `./scripts/show_latest_headline.sh --raw` 成功
- `./scripts/show_latest_headline.sh --source-check` 成功
- `git diff --check` 問題なし

**記録ファイル**
- `/home/runner/work/FlowSmith/FlowSmith/.agent/runs/masaakiayb-muselucid-project-template/20260220T021954Z-issue-3/coder_output_attempt_1.md` に実行ログと変更要約を記載済み。