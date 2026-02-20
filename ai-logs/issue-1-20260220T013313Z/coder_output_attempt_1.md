実装を完了しました。Issue #1 のスコープ内で最小構成で対応しています。

**変更内容**
- `scripts/show_latest_headline.sh` を新規追加
  - 単一ニュースソース（BBC RSS）から最新1件のヘッドラインを取得して表示
  - `--help` 実装
  - 失敗時に標準エラー出力 + 非0終了コード
    - `10`: ネットワーク/タイムアウト
    - `11`: HTTPエラー
    - `20`: パース失敗
    - `21`: ヘッドライン0件
- `README.md` を新規追加
  - 前提条件、実行方法、`--help`、終了コード方針を記載
  - 「最新」の定義（先頭 `item`）を明記

**検証結果**
- `./scripts/show_latest_headline.sh` → ヘッドライン1行出力、`0`
- `./scripts/show_latest_headline.sh >/tmp/headline.out && test -s /tmp/headline.out` → 成功
- `./scripts/show_latest_headline.sh --help` → ヘルプ表示、`0`
- 異常系確認:
  - `NEWS_FEED_URL='https://httpbin.org/status/404' ./scripts/show_latest_headline.sh` → エラーメッセージ、`11`
  - `NEWS_FEED_URL='https://httpbin.org/json' ./scripts/show_latest_headline.sh` → エラーメッセージ、`20`
- 品質ゲート: `git diff --check` → 問題なし

**実行ログ出力**
- `/home/runner/work/FlowSmith/FlowSmith/.agent/runs/masaakiayb-muselucid-project-template/20260220T013313Z-issue-1/coder_output_attempt_1.md` に記載済み。