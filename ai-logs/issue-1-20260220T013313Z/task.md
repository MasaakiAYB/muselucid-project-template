# Issue #1: 最新ニュースヘッドライン1件を取得して表示する

Project: (default)
Target repo: MasaakiAYB/muselucid-project-template
Target path: /home/runner/work/FlowSmith/FlowSmith/.agent/workspaces/masaakiayb-muselucid-project-template
URL: https://github.com/MasaakiAYB/muselucid-project-template/issues/1

## Body

Plan-ID: ISSUE-0001
Title: 最新ニュースヘッドライン1件を取得して表示する

### Goal / Summary
外部ニュースソースから最新のヘッドラインを1件取得し、実行結果として表示する最小機能を実装する。

### Scope
- ニュースソースを1つ選定し、ヘッドライン取得ロジックを実装する。
- 取得した最新ヘッドラインのタイトルを整形して表示する。
- 通信失敗・レスポンス不正時のエラーハンドリングを実装する。

### Non-goals
- 複数ニュースソースの横断取得
- 複数件の保存・履歴表示
- Web UI の実装

### Acceptance Criteria (DoD)
- 実行コマンドで最新ヘッドライン1件のタイトルが表示される。
- 取得失敗時に非0終了コードとエラーメッセージを返す。
- README に実行方法と前提条件が記載される。

### Verify
- ./scripts/show_latest_headline.sh
- ./scripts/show_latest_headline.sh >/tmp/headline.out && test -s /tmp/headline.out
- ./scripts/show_latest_headline.sh --help

### Constraints
- MVP は単一のニュースソースのみを対象にする。
- ニュース取得は公開フィードまたは無料 API を優先し、運用コストを抑える。
- ネットワーク障害時を考慮し、失敗時の終了コードとメッセージを明示する。

### Risk
low

### Depends On
- (none)


## External Feedback

_追加フィードバックなし_
