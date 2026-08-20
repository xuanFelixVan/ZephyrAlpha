# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_auction_book
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.miniqmt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] auction_book 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [TTL] permanent
"""auction_book 表 DDL-as-Code（category_id: market_auction_book, calc_mode: preload）。

本文件是 c1_market.auction_book 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_market_tables_ddl.py 执行。

补齐背景（裁定 #ARCH-SSOT-REFERENCE-INTEGRITY-001 Phase F 治本）：
    Phase 0 创建了 7 个缺失 schema 文件但遗漏 auction_book（表已存在但无 DDL 真源）。
    本文件补齐该 SSoT 缺口，并将引擎从 MergeTree 治本迁移到 ReplacingMergeTree
    （高频写入表，按 (symbol, trade_date, timestamp) 去重，避免写前 DELETE 开销）。

引擎选型说明：
    auction_book 是高频写入表（集合竞价 9:15-9:25 期间实时推送）。
    原引擎 MergeTree 需写前 DELETE WHERE date = today()（ch_writer.py §7.3），
    留下异步 mutations 记录累积，治本方案迁移到 ReplacingMergeTree 直接 INSERT，
    后台合并去重，无 DELETE 开销。
"""

from __future__ import annotations

# category_id: market_auction_book
# calc_mode: preload（集合竞价快照预加载到内存，回测时直接读取）

AUCTION_BOOK_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.auction_book
(
    trade_date   Date           COMMENT '交易日期',
    timestamp    DateTime64(3, 'Asia/Shanghai') COMMENT '快照时间戳(精确到秒)',
    symbol       String         COMMENT '证券代码',
    last_price   Decimal(18,4)  COMMENT '最新成交价',
    volume       UInt64         COMMENT '累计成交量(手)',
    amount       Decimal(18,2)  COMMENT '累计成交额(元)',
    open         Decimal(18,4)  COMMENT '当日开盘价',
    high         Decimal(18,4)  COMMENT '当日最高价',
    low          Decimal(18,4)  COMMENT '当日最低价',
    pre_close    Decimal(18,4)  COMMENT '昨收价',
    upper_limit  Decimal(18,4)  COMMENT '涨停价',
    lower_limit  Decimal(18,4)  COMMENT '跌停价',
    bid_price1   Decimal(18,4)  COMMENT '买一价',
    bid_price2   Decimal(18,4)  COMMENT '买二价',
    bid_price3   Decimal(18,4)  COMMENT '买三价',
    bid_price4   Decimal(18,4)  COMMENT '买四价',
    bid_price5   Decimal(18,4)  COMMENT '买五价',
    bid_volume1  UInt64         COMMENT '买一量(手)',
    bid_volume2  UInt64         COMMENT '买二量(手)',
    bid_volume3  UInt64         COMMENT '买三量(手)',
    bid_volume4  UInt64         COMMENT '买四量(手)',
    bid_volume5  UInt64         COMMENT '买五量(手)',
    ask_price1   Decimal(18,4)  COMMENT '卖一价',
    ask_price2   Decimal(18,4)  COMMENT '卖二价',
    ask_price3   Decimal(18,4)  COMMENT '卖三价',
    ask_price4   Decimal(18,4)  COMMENT '卖四价',
    ask_price5   Decimal(18,4)  COMMENT '卖五价',
    ask_volume1  UInt64         COMMENT '卖一量(手)',
    ask_volume2  UInt64         COMMENT '卖二量(手)',
    ask_volume3  UInt64         COMMENT '卖三量(手)',
    ask_volume4  UInt64         COMMENT '卖四量(手)',
    ask_volume5  UInt64         COMMENT '卖五量(手)',
    data_source  LowCardinality(String) COMMENT '数据来源(miniQMT)',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date, timestamp)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "auction_book"
DATABASE = "c1_market"
CATEGORY_ID = "market_auction_book"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(symbol, trade_date, timestamp)"

# 列清单（用于 INSERT 时显式指定）
INSERT_COLUMNS = (
    "(trade_date, timestamp, symbol, last_price, volume, amount, "
    "open, high, low, pre_close, upper_limit, lower_limit, "
    "bid_price1, bid_price2, bid_price3, bid_price4, bid_price5, "
    "bid_volume1, bid_volume2, bid_volume3, bid_volume4, bid_volume5, "
    "ask_price1, ask_price2, ask_price3, ask_price4, ask_price5, "
    "ask_volume1, ask_volume2, ask_volume3, ask_volume4, ask_volume5, "
    "data_source)"
)
