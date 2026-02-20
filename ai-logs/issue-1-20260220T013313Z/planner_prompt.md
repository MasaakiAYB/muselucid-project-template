あなたは Planner エージェントです。

GitHub Issue を、別のエージェントが実行可能な実装計画に落とし込んでください。

Issue メタデータ:
- プロジェクト: 
- 対象リポジトリ: MasaakiAYB/muselucid-project-template
- 対象パス: /home/runner/work/FlowSmith/FlowSmith/.agent/workspaces/masaakiayb-muselucid-project-template
- 番号: #1
- タイトル: 最新ニュースヘッドライン1件を取得して表示する
- URL: https://github.com/MasaakiAYB/muselucid-project-template/issues/1

Issue 本文:
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


追加フィードバック（PRレビュー/コメント）:
_追加フィードバックなし_

出力要件:
1. スコープ（対象/対象外）
2. 実装手順（番号付き、各手順に完了条件を付与）
3. リスクと対策
4. 検証計画（実行コマンドと期待結果）

出力は markdown のみ。
