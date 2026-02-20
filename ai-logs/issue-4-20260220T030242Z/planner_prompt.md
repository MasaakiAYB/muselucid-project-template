あなたは Planner エージェントです。

GitHub Issue を、別のエージェントが実行可能な実装計画に落とし込んでください。

Issue メタデータ:
- プロジェクト: 
- 対象リポジトリ: MasaakiAYB/muselucid-project-template
- 対象パス: /home/runner/work/FlowSmith/FlowSmith/.agent/workspaces/masaakiayb-muselucid-project-template
- 番号: #4
- タイトル: READMEと検証手順を整備する
- URL: https://github.com/MasaakiAYB/muselucid-project-template/issues/4

Issue 本文:
Plan-ID: ISSUE-0003
Title: READMEと検証手順を整備する

### Goal / Summary
実装済み機能を誰でも再現できるように、実行方法と検証手順をREADMEに反映する。

### Scope
- READMEに前提条件、実行方法、検証方法を追記する。
- 失敗時の確認ポイントを簡潔に記載する。
- CIまたはローカル検証コマンドを明示する。

### Non-goals
- 機能追加
- デプロイ手順の実装
- 運用監視の導入

### Acceptance Criteria (DoD)
- READMEの手順だけで機能確認が再現できる。
- 最低1つの検証コマンドが明記されている。
- 実装内容とREADME記載に矛盾がない。

### Verify
- rg -n \"latest|headline|ニュース|ヘッドライン\" README.md
- ./scripts/show_latest_headline.sh >/tmp/headline.out && test -s /tmp/headline.out
- test -f README.md

### Constraints
- MVP は単一のニュースソースのみを対象にする。
- ニュース取得は公開フィードまたは無料 API を優先し、運用コストを抑える。
- ネットワーク障害時を考慮し、失敗時の終了コードとメッセージを明示する。

### Risk
low

### Depends On
- ISSUE-0002


追加フィードバック（PRレビュー/コメント）:
_追加フィードバックなし_

出力要件:
1. スコープ（対象/対象外）
2. 実装手順（番号付き、各手順に完了条件を付与）
3. リスクと対策
4. 検証計画（実行コマンドと期待結果）

出力は markdown のみ。
