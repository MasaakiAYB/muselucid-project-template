あなたは Coder エージェントです。

リポジトリ: /home/runner/work/FlowSmith/FlowSmith/.agent/workspaces/masaakiayb-muselucid-project-template
プロジェクト: 
対象リポジトリ: MasaakiAYB/muselucid-project-template
ブランチ: agent/issue-1-1
試行: 1/3

Issue:
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

計画:
## 1. スコープ（対象/対象外）

### 対象
- 単一ニュースソース（公開RSSまたは無料API）から「最新1件」を取得するCLIスクリプトを実装する。
- 取得結果からヘッドラインタイトルのみを整形して標準出力へ表示する。
- 通信失敗・HTTPエラー・レスポンス形式不正・空データ時に、エラーメッセージを標準エラー出力へ表示し非0終了する。
- `--help` オプションを実装する。
- READMEに前提条件、実行方法、失敗時挙動を記載する。

### 対象外
- 複数ニュースソースの切り替え/横断取得
- 複数件表示、保存、履歴管理
- Web UI、常駐処理、スケジューラ連携

---

## 2. 実装手順（番号付き、各手順に完了条件付き）

1. ニュースソースと取得方式を確定する（公開RSS優先、APIキー不要を優先）。
完了条件: 利用URL・データ形式（XML/JSON）・利用理由（無料/安定/キー不要）をREADME下書きに明記できる。

2. `scripts/show_latest_headline.sh` を新規作成し、CLI骨格を実装する。
完了条件: `--help` で使用方法を表示し、通常実行時の処理フロー（取得→抽出→表示）に入る。

3. ヘッドライン取得ロジックを実装する（例: `curl` + パーサ）。
完了条件: 正常レスポンス時に最新1件のタイトル文字列のみを標準出力へ1行で出力できる。

4. エラーハンドリングを実装する（終了コードを明確化）。
完了条件: 以下を判別して非0終了できる。
- ネットワーク/タイムアウト
- HTTPステータス異常
- 解析失敗（形式不正）
- ヘッドライン0件

5. READMEを作成または更新する。
完了条件: 前提コマンド（例: `bash`, `curl`, `xmllint`/`jq` など）、実行例、`--help`、代表的な失敗時メッセージと終了コード方針を記載する。

6. 実行確認と最終調整を行う。
完了条件: Issue記載のVerifyコマンドがすべて通り、DoD 3項目を満たす。

---

## 3. リスクと対策

- リスク: 無料ニュースソースのレスポンス形式変更でパースが壊れる。  
対策: パーサ依存を最小化し、必須フィールド欠落時は明示エラーにする。READMEに対象ソース固定を明記する。

- リスク: CI/実行環境にXML/JSONパーサがない。  
対策: 依存を最小にする（可能ならPOSIX + `curl`中心）。追加依存が必要な場合はREADMEに必須として明記する。

- リスク: 一時的なネットワーク障害で不安定。  
対策: `curl` にタイムアウト・リトライ（最小回数）を設定し、最終的に失敗時は非0終了と短い原因メッセージを返す。

- リスク: 「最新」の定義ずれ（配信順/公開時刻順）。  
対策: 採用ソースの先頭要素を「最新」と定義しREADMEに明記する。

---

## 4. 検証計画（実行コマンドと期待結果）

1. `./scripts/show_latest_headline.sh`  
期待結果: 標準出力にヘッドラインタイトル1行が表示され、終了コード0。

2. `./scripts/show_latest_headline.sh >/tmp/headline.out && test -s /tmp/headline.out`  
期待結果: コマンド成功（終了コード0）、`/tmp/headline.out` が空でない。

3. `./scripts/show_latest_headline.sh --help`  
期待結果: 使い方、オプション、前提条件が表示され、終了コード0。

4. 異常系確認（例: 一時的にURLを無効値へ変更して実行）  
期待結果: 標準エラー出力に原因メッセージ、終了コードは非0。

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

編集後、`/home/runner/work/FlowSmith/FlowSmith/.agent/runs/masaakiayb-muselucid-project-template/20260220T013313Z-issue-1/coder_output_attempt_1.md` に実行ログと変更ファイル要約を短く記載してください。
