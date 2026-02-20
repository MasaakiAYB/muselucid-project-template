# muselucid-project-template

単一ニュースソースから最新ヘッドライン1件を表示する最小CLIです。

## ニュースソース
- URL: `https://feeds.bbci.co.uk/news/rss.xml`
- 形式: RSS (XML)
- 選定理由: APIキー不要、無料で取得可能

最新の定義は「フィード先頭の最初の `item` の `title`」です。

## 前提条件
- `bash`
- `curl`
- `python3`（標準ライブラリの XML パーサを使用）

## 実行方法
```bash
./scripts/show_latest_headline.sh
```

標準出力にヘッドラインタイトル1行を表示します。

## 検証手順（ローカル）
README の手順だけで動作確認できるよう、以下を順に実行します。

1. README の関連記述確認
```bash
rg -n "latest|headline|ニュース|ヘッドライン" README.md
```
期待結果: 実行方法・検証方法・失敗時確認に関する記述がヒットする。

2. 正常系（見出しを1件取得）
```bash
./scripts/show_latest_headline.sh >/tmp/headline.out && test -s /tmp/headline.out
```
期待結果: 終了コード `0`。`/tmp/headline.out` が空でない。

3. README ファイル存在確認
```bash
test -f README.md
```
期待結果: 終了コード `0`。

4. 失敗系（ネットワーク障害相当）
```bash
NEWS_FEED_URL="https://example.invalid/rss.xml" ./scripts/show_latest_headline.sh >/tmp/headline.out 2>/tmp/headline.err; echo $?
```
期待結果: 終了コード `10`。`/tmp/headline.err` に `network or timeout error` を含む。

5. 失敗系（解析不能データ）
```bash
NEWS_FEED_URL="https://example.com" ./scripts/show_latest_headline.sh >/tmp/headline.out 2>/tmp/headline.err; echo $?
```
期待結果: 終了コード `20` または `21`。`/tmp/headline.err` に `failed to parse` または `no headline found` を含む。

## ヘルプ
```bash
./scripts/show_latest_headline.sh --help
```

## 終了コード
- `0`: 成功
- `2`: 不正な引数
- `10`: ネットワーク/タイムアウトで取得失敗
- `11`: HTTPエラーで取得失敗
- `20`: レスポンスの解析失敗
- `21`: ヘッドライン0件

## 取得元URLの上書き
MVP は単一ニュースソースを対象としており、デフォルトは `https://feeds.bbci.co.uk/news/rss.xml` のみです。検証時などに `NEWS_FEED_URL` で取得先を変更できます。

```bash
NEWS_FEED_URL="https://example.invalid/rss.xml" ./scripts/show_latest_headline.sh
```

## 失敗時の確認ポイント
- `10`: ネットワーク/タイムアウト。URL の到達性、DNS、プロキシ設定、`stderr` の `network or timeout error` を確認。
- `11`: HTTP エラー。URL のタイプミス、アクセス権、`stderr` の `HTTP error` を確認。
- `20`: レスポンス解析失敗。取得データが XML として不正、`python3` の利用可否、`stderr` の `failed to parse` を確認。
- `21`: ヘッドライン未検出。RSS/Atom の `item/title` または `entry/title` が存在するか、`stderr` の `no headline found` を確認。
