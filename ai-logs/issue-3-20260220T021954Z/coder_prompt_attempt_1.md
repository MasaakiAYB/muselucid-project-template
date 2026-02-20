あなたは Coder エージェントです。

リポジトリ: /home/runner/work/FlowSmith/FlowSmith/.agent/workspaces/masaakiayb-muselucid-project-template
プロジェクト: 
対象リポジトリ: MasaakiAYB/muselucid-project-template
ブランチ: agent/issue-3-cli
試行: 1/3

Issue:
- 番号: #3
- タイトル: 取得したヘッドラインをCLIで表示する
- URL: https://github.com/MasaakiAYB/muselucid-project-template/issues/3

Issue 本文:
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


追加フィードバック（PRレビュー/コメント）:
_追加フィードバックなし_

計画:
## 1. スコープ（対象/対象外）

**対象（In Scope）**
- ISSUE-0001 で実装済みの「最新ヘッドライン取得処理」を呼び出し、CLI向けに1件表示する。
- 標準出力向けの表示フォーマットを関数化して分離する。
- 取得失敗・表示失敗時に、標準エラー出力へ明確なメッセージを出し、非0終了コードで終了する。
- 実行エントリは `./scripts/show_latest_headline.sh` を維持する。

**対象外（Out of Scope）**
- ヘッドライン複数件表示。
- 色付け・装飾などのリッチ表示。
- Web UI や API サーバー化。
- ニュースソース追加（単一ソースのまま）。

## 2. 実装手順（番号付き、各手順に完了条件）

1. 現行取得処理（ISSUE-0001）のI/F確認と固定化  
完了条件: 「成功時の取得結果形式」と「失敗時の戻り値/エラー出力」が明文化され、表示側が依存する入力仕様が確定している。

2. 表示専用関数を追加  
完了条件: 例として `format_headline()` と `print_headline()` のような関数が分離され、取得ロジックと直接混在していない。

3. `show_latest_headline.sh` のメインフローを整理  
完了条件: `main` が「取得 -> 整形 -> 出力」の順で接続され、ISSUE-0001の取得関数（または `--raw` 出力）を実際に利用している。

4. エラーハンドリングを統一  
完了条件: 取得失敗時・整形不能時・出力失敗時の各ケースで、標準エラーに原因付きメッセージを出し、終了コードが非0になる。

5. 出力フォーマットの最小仕様を確定  
完了条件: 最新1件が毎回同じ形式で表示される（例: タイトル必須、必要なら公開日時/ソース名を固定順で1件表示）。

6. Verifyコマンドを通す  
完了条件: Issue記載の3コマンドが期待どおり成功し、標準出力/標準エラーの有無と終了コードが要件を満たす。

## 3. リスクと対策

- リスク: ISSUE-0001の取得出力が未固定で、表示側が壊れやすい。  
対策: 取得側I/Fを最初に固定し、表示側はそのI/Fのみを参照する。

- リスク: ネットワーク障害時に空出力で終了してしまう。  
対策: 取得失敗を必ず検知し、空出力を正常扱いしない（非0 + stderr必須）。

- リスク: シェル実装でパイプ失敗を取りこぼす。  
対策: `set -euo pipefail` 相当の方針で実装し、各関数の戻り値を明示チェックする。

- リスク: 将来拡張時に表示ロジックが肥大化。  
対策: 整形関数と出力関数を分離し、入力を「ヘッドライン1件構造」に限定する。

## 4. 検証計画（実行コマンドと期待結果）

1. `./scripts/show_latest_headline.sh`  
期待結果: 最新ヘッドライン1件が標準出力に表示され、終了コード `0`。

2. `./scripts/show_latest_headline.sh >/tmp/headline.out && test -s /tmp/headline.out`  
期待結果: `/tmp/headline.out` が空でない（1件表示できている）、コマンド全体成功。

3. `./scripts/show_latest_headline.sh 2>/tmp/headline.err || test -s /tmp/headline.err`  
期待結果:  
- 正常系なら前半が成功（`headline.err` は空でも可）。  
- 異常系なら後半が成功し、`/tmp/headline.err` に原因メッセージが出力される。  
- 異常系の終了コードは非0。

前回試行のフィードバック:
None

必須の品質ゲート:
- `git diff --check`

ルール:
- 変更は最小限にし、Issue のスコープに集中すること。
- テストが不足している場合は、可能な範囲で追加または更新すること。
- 無関係なファイルは変更しないこと。
- UI変更（画面見た目/レイアウト/スタイル/フロントUI部品）を含む場合は、変更箇所のスクリーンショットまたはアニメーションGIF（`.png/.jpg/.jpeg/.webp/.gif`）を `/home/runner/work/FlowSmith/FlowSmith/.agent/workspaces/masaakiayb-muselucid-project-template/.flowsmith/ui-evidence` に保存すること（対象リポジトリ配下。artifact-only モードではコミット前に自動で除外される）。
- UI証跡画像は実画面キャプチャを使用し、文字が判読可能であること。日本語文字を含む場合は文字化けしていないこと。プレースホルダ画像（矩形塗りつぶし等）で代替しないこと。

編集後、`/home/runner/work/FlowSmith/FlowSmith/.agent/runs/masaakiayb-muselucid-project-template/20260220T021954Z-issue-3/coder_output_attempt_1.md` に実行ログと変更ファイル要約を短く記載してください。
