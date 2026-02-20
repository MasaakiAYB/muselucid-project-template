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

### 対象
- `scripts/show_latest_headline.sh` で最新ヘッドライン1件を標準出力に表示する。
- ISSUE-0001の取得処理（最新1件の取得結果）を表示処理に接続する。
- 表示処理を関数分離し、将来の拡張（複数件表示など）に備える。
- 失敗時に明確なエラーメッセージを標準エラー出力へ出し、非0終了コードを返す。

### 対象外
- 複数件表示。
- 色付き/リッチなCLI表示。
- Web UIやAPIサーバ実装。
- 複数ニュースソース対応。

---

## 2. 実装手順（番号付き、各手順に完了条件を付与）

1. **ISSUE-0001の取得I/Fを確認し、受け渡し形式を固定する**  
完了条件: 「取得関数が返すデータ形式（例: `title/link/published_at/source`）」と「失敗時の戻り値・stderr方針」が `show_latest_headline.sh` 内で一貫している。

2. **表示専用関数を実装/整理する（関数分離）**  
完了条件: 表示整形を担当する関数（例: `format_headline`）と出力関数（例: `print_headline`）が分離され、`main` から呼ばれる構成になっている。

3. **取得処理と表示処理を接続する**  
完了条件: `main` で「取得 → 整形 → 出力」の順で実行され、正常時は最新ヘッドライン1件が標準出力に出る。

4. **異常系ハンドリングを明確化する**  
完了条件: ネットワーク失敗・空レスポンス・パース失敗・必須項目欠落時に、`ERROR: ...`形式など明確なstderrを出し、終了コードが非0になる。

5. **CLIオプション/使い方の整合性を確認する**  
完了条件: 不正オプション時にusageを表示し、終了コードを区別（例: usageエラー=2、実行エラー=1）できる。

6. **最小限の実行検証を行う**  
完了条件: Verifyにある3コマンドで、正常系と異常系（stderr/終了コード）が再現できる。

---

## 3. リスクと対策

- **リスク: RSS/XML構造の揺らぎでパース失敗**  
  対策: 最低限 `title` 必須チェックを入れ、失敗時は即エラー終了。パース箇所は関数内に閉じる。

- **リスク: ネットワーク一時障害で不安定**  
  対策: `curl` にタイムアウトを設定し、接続失敗メッセージを明示。終了コード1を返す。

- **リスク: 取得処理と表示処理の責務混在**  
  対策: 取得・整形・出力を関数分離し、`main` はオーケストレーションのみ担当。

- **リスク: 非0終了コードがケースごとにぶれる**  
  対策: usageエラーと実行エラーのコード方針を固定し、分岐ごとに明示的に `return`。

---

## 4. 検証計画（実行コマンドと期待結果）

1. `./scripts/show_latest_headline.sh`  
期待結果: 標準出力に最新ヘッドライン1件が見やすい形式で表示され、終了コード0。

2. `./scripts/show_latest_headline.sh >/tmp/headline.out && test -s /tmp/headline.out`  
期待結果: `/tmp/headline.out` が空でない（表示文字列が出力されている）。

3. `./scripts/show_latest_headline.sh 2>/tmp/headline.err || test -s /tmp/headline.err`  
期待結果: 異常時は終了コード非0で、`/tmp/headline.err` に原因が分かるエラーメッセージが出る。正常時はこの検証はスキップ可（再現時のみ確認）。

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

編集後、`/home/runner/work/FlowSmith/FlowSmith/.agent/runs/masaakiayb-muselucid-project-template/20260220T022401Z-issue-3/coder_output_attempt_1.md` に実行ログと変更ファイル要約を短く記載してください。
