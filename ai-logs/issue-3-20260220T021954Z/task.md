# Issue #3: 取得したヘッドラインをCLIで表示する

Project: (default)
Target repo: MasaakiAYB/muselucid-project-template
Target path: /home/runner/work/FlowSmith/FlowSmith/.agent/workspaces/masaakiayb-muselucid-project-template
URL: https://github.com/MasaakiAYB/muselucid-project-template/issues/3

## Body

Plan-ID: ISSUE-0002
Title: 取得したヘッドラインをCLIで表示する

### Goal / Summary
ISSUE-0001で取得したデータを使い、ユーザー向けの標準出力フォーマットを実装する。

### Scope
- 最新ヘッドライン1件を見やすい形式で標準出力に表示する。
- 出力失敗時のエラーメッセージを明確にする。
- 将来の拡張に備えて表示処理を関数分離する。

### Non-goals
- 複数件表示
- カラー表示やリッチフォーマット
- Web UI 表示

### Acceptance Criteria (DoD)
- コマンド実行時に最新ヘッドライン1件が標準出力に表示される。
- 表示処理がISSUE-0001の取得処理に接続されている。
- 異常系で非0終了コードが返る。

### Verify
- ./scripts/show_latest_headline.sh
- ./scripts/show_latest_headline.sh >/tmp/headline.out && test -s /tmp/headline.out
- ./scripts/show_latest_headline.sh 2>/tmp/headline.err || test -s /tmp/headline.err

### Constraints
- MVP は単一のニュースソースのみを対象にする。
- ニュース取得は公開フィードまたは無料 API を優先し、運用コストを抑える。
- ネットワーク障害時を考慮し、失敗時の終了コードとメッセージを明示する。

### Risk
low

### Depends On
- ISSUE-0001


## External Feedback

_追加フィードバックなし_
