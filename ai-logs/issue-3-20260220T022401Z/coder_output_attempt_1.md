実施結果として、Issue #3 は現状コードで要件を満たしていました。追加のコード修正はしていません。

確認した内容:
- `scripts/show_latest_headline.sh` は `fetch_latest_headline_raw` / `format_headline` / `print_headline` に関数分離済み
- 取得処理（ISSUE-0001相当）と表示処理は `main` で接続済み
- 異常系は `ERROR: ...` を stderr に出し、非0終了（不正オプション時は `2`、実行エラーは `1`）

検証結果:
- `./scripts/show_latest_headline.sh` -> 最新ヘッドライン1件を標準出力、終了コード `0`
- `./scripts/show_latest_headline.sh >/tmp/headline.out && test -s /tmp/headline.out` -> 成功、出力ファイル非空
- `./scripts/show_latest_headline.sh 2>/tmp/headline.err || test -s /tmp/headline.err` -> 正常系のため終了コード `0`（stderrなし）
- 追加異常系: `./scripts/show_latest_headline.sh --bad` -> stderr に明確なエラーと usage、終了コード `2`
- 品質ゲート: `git diff --check` -> 問題なし

実行ログは指定先に記録済みです:
- `/home/runner/work/FlowSmith/FlowSmith/.agent/runs/masaakiayb-muselucid-project-template/20260220T022401Z-issue-3/coder_output_attempt_1.md`