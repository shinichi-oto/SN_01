# Crawler_System
## ver.01

## 説明
- このクローラは指定サイト内のタイトル、テキストを取得し、SQLサーバに格納します*1。
- 形式通りにサイトのTitle,ContentTAG,URLを指定した .xlsx ファイルからの読み込み可能
- クローリング速度はコード上2秒に設定してありますが、対象サイトのサーバー負荷を考慮して10秒前後に設定した方がよいです*2。
- システム内にTransformerを使用した翻訳及び要約システムを導入してあります。メインシステムに適用してあるTransformerはhuggingfaceを使用したシステムであり、要約はPegusus、翻訳はmbert-mtmを使用してありますが、Transformerディレクトリ内に英日Vocab作成class,マルチヘッドアテンション機構構築classがありますので、GPUが使用できる環境及び翻訳テキストコーパスを所持している場合に実行可能となっています。このディレクトリ内にある[テキストコーパス](http://www.manythings.org/anki/)は8万程しかありませんので効果量は低いです。
- *1 : 事前にSQLサーバのSTART及び、指定してある形式通りにSLQを構築しておかなければ動作しません。
- *2 : 高速でクローリングすると対象サイトへの負荷に繋がり、場合によってはIPlock、法的措置を講じられる場合がありますので高速クローリングはお勧めしません。


## **機能**
    $ python console.py <arg> start
    -m    : マルチクローリング可能なメインクローラシステム
    -s    : 対象サイト内でのサーチ
    -n    : NgramSystem, WordCloud対応
    -nsum : NgramSummarySystem, Transformer、Pegusus-xsum(抽象型モデル)を使用した要約に対応
    -nj   : NgtamSystem日本語翻訳対応、　mbart-large-50-many-to-manyを使用
    -ns   : -nsum -nj を同時実行する。つまり、出力される要約を日本語へ翻訳する。これは環境によって動作が非常に遅い。

## **SQL Table**
    
    DATABASE        : Webscraping
    website         : id(int NO PRI NULL auto_increment) middle_table_id(int NO NULL) title(varchar(300) YES NULL) content(mediumtext YES NULL) timestamp(timestamp YES NULL) created(timestamp YES NULL CURRENT_TIMESTAMP DEFAULT_GENERATED) url(varchar(300) YES NULL)
    country_code    : id(int No PRI NULL auto_increment) country(varchar(200) NO PRI NULL)
    website_id      : id(int NO PRI NULL auto_increment) website_name(varchar(200) NO NULL) web_URL(varchar(200) NO NULL)
    news_categories : id(int NO PRI NULL auto_increment) category_tag(varchar(200) NO NULL)
    middle_table    : id(int NO PRI NULL auto_increment) country_code(int NO NULL) website_id(int NO NULL) nwes_categories(int NO NULL)
    page_url        : id(bigint NO NULL auto_incremetnt) url(varchar(200) NO NULL)    

## 仮想環境ライブラリ

    - Anaconda
    .ymlファイルを使用して仮想環境の構築を行ってください。
    
    $ conda create -n <env> -f <file>.yml

## SITE_TAG

    COUTRY     : COUNTRY
    SITE       : SITE_NAME
    URL        : WEB_SITE_URL
    CONT       : SITE_TAG_CONTENT_CATEGORIE
    TAG T      : TITLE_TAG
    TAG C      : CONTENT_TAG
    SEARCHURL  : WEB_SITE_SEARCH_URFL
    
    siteData = [
        ['<COUNTRY>', '<SITE>', '<URL>', '^(/<CONT>/)', False,
        '<TAG: T>', '<TAG: C>'],
    ]


    searchSiteData = [
        ['<SEARCH:URL>', '<TAG>',
        '<TAG:SEARCH>', False, '<URL>',
        '<TAG: T>', '<TAG: C>'
        ],
    ]
    
## SQLServer
    
    <password> : SLQ_SERVER_PASSWORD
    
    pymysql.connect(host='127.0.0.1', port=3306,
                           user='root', password='<password>',
                           db='mysql', charset='utf8mb4')
                           
## SITE_LOGIN
    
    <ID>       : LOGIN_ID
    <PASSWORD> : LOGIN_PASSWORD
    
    def getURLBS_a(self, pageUrl):
        session = requests.Session()
        params = {'email': '<ID>', 'password': '<password>'}
        session.post('<LOGIN:URL>', data=params)
        ...
