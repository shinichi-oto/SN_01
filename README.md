# Crawler_System

## 説明
---
>このクローラは指定サイト内のタイトル、テキストを取得し、SQLサーバに格納します*1。
>形式通りにサイトのTitle,ContentTAG,URLを指定した .xlsx ファイルからの読み込み可能
>*1 : 指定してある形式通りにSLQを構築しておかなければ動作しません。
---
## 機能
> $ python console.py <arg> start
> -m    : マルチクローリング可能なメインクローラシステム
> -s    : 対象サイト内でのサーチ,　WordCloud対応
> -n    : NgramSystem
> -nsum : NgramSummarySystem, Transformer、Pegusus-xsum(抽象型モデル)を使用した要約に対応
> -nj   : NgtamSystem日本語翻訳対応、　mbart-large-50-many-to-manyを使用
> -ns   : -nsum -nj を同時実行する。つまり、出力される要約を日本語へ翻訳する。これは環境によって動作が非常に遅い。
---
