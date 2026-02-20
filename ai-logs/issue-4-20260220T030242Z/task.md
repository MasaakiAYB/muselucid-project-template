# Issue #4: READMEと検証手順を整備する

Project: (default)
Target repo: MasaakiAYB/muselucid-project-template
Target path: /home/runner/work/FlowSmith/FlowSmith/.agent/workspaces/masaakiayb-muselucid-project-template
URL: https://github.com/MasaakiAYB/muselucid-project-template/issues/4

## Body

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


## External Feedback

_追加フィードバックなし_
