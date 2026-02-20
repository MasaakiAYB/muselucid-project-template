## 1. スコープ（対象/対象外）

**対象**
- `README.md` に以下を実装と一致する形で明記する。  
  - 前提条件（`bash` `curl` `python3`）
  - 実行方法（`./scripts/show_latest_headline.sh`）
  - 検証方法（ローカル実行コマンド）
  - 失敗時の確認ポイント（終了コードとエラーメッセージの見方）
- 単一ニュースソース（`NEWS_FEED_URL` デフォルト1件）前提を明示する。
- ネットワーク障害時の終了コード・メッセージを README 上で確認可能にする。

**対象外**
- 新機能追加（CLI仕様変更、複数ソース対応など）
- デプロイ手順の新設
- 運用監視・CI機能そのものの追加（READMEへの記載のみ）

## 2. 実装手順（番号付き、各手順の完了条件付き）

1. 現行実装との差分確認を行う。  
完了条件: `scripts/show_latest_headline.sh` の仕様（引数、環境変数、終了コード、エラーメッセージ）を一覧化し、README反映対象が確定している。

2. README の構成を整理し、再現手順を「前提条件→実行→検証→失敗時確認」の順に並べる。  
完了条件: 初見ユーザーが README の上から順に実行するだけで機能確認できる章立てになっている。

3. 検証手順セクションを追加/更新し、ローカル検証コマンドを明示する。  
完了条件: 少なくとも1つ以上の検証コマンドが明記され、実行結果の期待値（成功時/失敗時）が記述されている。

4. 失敗時の確認ポイントを追記し、終了コードとの対応を明確化する。  
完了条件: `10/11/20/21` の意味と代表的な確認方法（URL、依存コマンド、stderr確認）がREADMEに記載されている。

5. 実装とREADMEの整合性チェックを実施する。  
完了条件: README記載のコマンドを実行して矛盾がなく、IssueのDoD 3項目を満たすことを確認できる。

## 3. リスクと対策

- リスク: README の終了コード説明が実装とずれる。  
対策: `scripts/show_latest_headline.sh` の `usage` と実際の `exit` 分岐を基準に記載する。

- リスク: ネットワーク依存で検証が不安定。  
対策: 検証手順に「成功系」と「失敗系（`NEWS_FEED_URL` 上書き）」を分けて記載し、失敗時でも期待される終了コードで判定する。

- リスク: CIが機能検証を自動実行していないため再現性がぶれる。  
対策: 今回は非ゴールとしてCI追加は行わず、READMEにローカル検証コマンドを明示して再現手順を固定する。

## 4. 検証計画（実行コマンドと期待結果）

1. README内の関連記述確認  
```bash
rg -n "latest|headline|ニュース|ヘッドライン" README.md
```  
期待結果: 実行方法・検証方法・失敗時説明に関連する行がヒットする。

2. 正常系の出力確認  
```bash
./scripts/show_latest_headline.sh >/tmp/headline.out && test -s /tmp/headline.out
```  
期待結果: 終了コード `0`、`/tmp/headline.out` が空でない（1行以上の見出し）。

3. READMEファイル存在確認  
```bash
test -f README.md
```  
期待結果: 終了コード `0`。

4. 失敗系（ネットワーク障害相当）の確認  
```bash
NEWS_FEED_URL="https://example.invalid/rss.xml" ./scripts/show_latest_headline.sh >/tmp/headline.out 2>/tmp/headline.err; echo $?
```  
期待結果: 終了コード `10`、`/tmp/headline.err` に network/timeout 系エラーメッセージ。

5. 失敗系（解析不能データ）の確認  
```bash
NEWS_FEED_URL="https://example.com" ./scripts/show_latest_headline.sh >/tmp/headline.out 2>/tmp/headline.err; echo $?
```  
期待結果: 終了コード `20` または `21`、`/tmp/headline.err` に parse/no headline 系メッセージ。