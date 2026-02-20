README を Issue #4 のスコープに合わせて更新し、実装と整合する検証手順を追加しました。

変更内容:
- `README.md`
  - 前提条件・実行方法に続く形で `検証手順（ローカル）` を追加
  - 以下の検証コマンドと期待結果を明記
    - `rg -n "latest|headline|ニュース|ヘッドライン" README.md`
    - `./scripts/show_latest_headline.sh >/tmp/headline.out && test -s /tmp/headline.out`
    - `test -f README.md`
    - `NEWS_FEED_URL="https://example.invalid/rss.xml" ...`（終了コード `10`）
    - `NEWS_FEED_URL="https://example.com" ...`（終了コード `20` または `21`）
  - MVP が単一ニュースソース前提であることを明記
  - 失敗時の確認ポイントとして終了コード `10/11/20/21` の見方を追記

検証結果:
- `rg -n "latest|headline|ニュース|ヘッドライン" README.md` -> ヒットあり
- `./scripts/show_latest_headline.sh >/tmp/headline.out && test -s /tmp/headline.out` -> `0`
- `test -f README.md` -> `0`
- `NEWS_FEED_URL="https://example.invalid/rss.xml" ./scripts/show_latest_headline.sh ...` -> `10`（`network or timeout error` 確認）
- `NEWS_FEED_URL="https://example.com" ./scripts/show_latest_headline.sh ...` -> `20`（`failed to parse feed response` 確認）
- `git diff --check` -> 問題なし

実行ログを記録済み:
- `/home/runner/work/FlowSmith/FlowSmith/.agent/runs/masaakiayb-muselucid-project-template/20260220T030242Z-issue-4/coder_output_attempt_1.md`