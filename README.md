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
検証時などに `NEWS_FEED_URL` で取得先を変更できます。

```bash
NEWS_FEED_URL="https://example.invalid/rss.xml" ./scripts/show_latest_headline.sh
```
