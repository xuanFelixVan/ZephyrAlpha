# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_tick_depth_5
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_schema.py; zephyr.data.tick_subscriber; scripts/ch/apply_market_tables_ddl.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] tick_depth_5 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [TTL] permanent
"""tick_depth_5 表 DDL-as-Code（category_id: market_tick_depth_5，五档盘口落库，裁定⑤ 2026-09-09）。

本文件是 c1_market.tick_depth_5 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

背景（台账 §8.3.1 裁定⑤ + §8.6 任务一，2026-09-09）：
    CH tick_data 按表结构只落 1 档（tick_to_row 取 [0]，设计如此），但数据流里
    五档全在（桥 v19 25 列 dump 与 miniqmt 推送都带完整 bid1-5/ask1-5/bidVol1-5/
    askVol1-5，Redis 热缓存已存完整五档，仅 CH 落库时丢弃）。本表以并行旁路
    （tick_subscriber 桥模式新增落盘分支）承接五档深度，现有 tick_data 链路
    零变更（红线 2：TICK_SOURCE 运行链行为不变）。

设计决策（对齐 market_tick.py，裁定 #ARCH-CH-002/#ARCH-CH-022 沿用）：
1. ORDER BY 5 字段 (market_type, symbol, trade_date, timestamp, price)
   - 与 tick_data 同构：同时间戳不同价位的快照不被 ReplacingMergeTree 合并
2. PARTITION BY toYYYYMM(trade_date) 月级分区（同 tick_data 理由）
3. ReplacingMergeTree（无版本列）——(symbol, timetag) 桥侧去重 + 重复导入行合并
4. 五档 20 列 Nullable（bid_price1..5/ask_price1..5/bid_volume1..5/ask_volume1..5）
   - miniqmt 历史回填的 19 列 tick 也带完整五档；更早历史（bdpan 等）无五档，
     本表不回填那些行（缺档留 NULL，如实登记：深史五档任何渠道都不存在）
5. 时区防线（#ARCH-CH-022）：timestamp DateTime64(3, 'Asia/Shanghai')；
     recorded_time/ingest_ts DateTime64(3, 'UTC') DEFAULT now()
6. 跳过索引 idx_ts/idx_symbol 同 tick_data（ORDER BY 前缀是 market_type，
     单标点查靠 set(10000) 索引裁剪）
7. exchange/symbol_canonical MATERIALIZED 派生列与 tick_data 同式（TRAE-082
     跨表 JOIN 一致性；MATERIALIZED 零写入成本）
"""

from __future__ import annotations

# category_id: market_tick_depth_5
# calc_mode: replay（与 tick_data 同语义：回测逐条回放）

TICK_DEPTH_5_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.tick_depth_5
(
    trade_date    Date                    COMMENT '交易日期',
    timestamp     DateTime64(3, 'Asia/Shanghai') COMMENT '时间戳(3秒粒度快照)',
    recorded_time DateTime64(3, 'UTC')  DEFAULT now() COMMENT '录制器本地接收时间(用于延迟分析)',
    symbol        String                  COMMENT '证券代码',
    market_type   LowCardinality(String)  COMMENT '市场类型(A_share/futures/index)',
    price         Decimal(18,4)           COMMENT '成交价(快照最新价)',
    volume        UInt64                  COMMENT '成交量(股,快照累计)',
    amount        Decimal(18,2)           COMMENT '成交额(元,快照累计)',
    data_source   LowCardinality(String) DEFAULT 'miniqmt' COMMENT '数据来源',
    bid_price1    Nullable(Decimal(18,4)) COMMENT '买一价',
    bid_price2    Nullable(Decimal(18,4)) COMMENT '买二价',
    bid_price3    Nullable(Decimal(18,4)) COMMENT '买三价',
    bid_price4    Nullable(Decimal(18,4)) COMMENT '买四价',
    bid_price5    Nullable(Decimal(18,4)) COMMENT '买五价',
    ask_price1    Nullable(Decimal(18,4)) COMMENT '卖一价',
    ask_price2    Nullable(Decimal(18,4)) COMMENT '卖二价',
    ask_price3    Nullable(Decimal(18,4)) COMMENT '卖三价',
    ask_price4    Nullable(Decimal(18,4)) COMMENT '卖四价',
    ask_price5    Nullable(Decimal(18,4)) COMMENT '卖五价',
    bid_volume1   Nullable(UInt64)        COMMENT '买一量',
    bid_volume2   Nullable(UInt64)        COMMENT '买二量',
    bid_volume3   Nullable(UInt64)        COMMENT '买三量',
    bid_volume4   Nullable(UInt64)        COMMENT '买四量',
    bid_volume5   Nullable(UInt64)        COMMENT '买五量',
    ask_volume1   Nullable(UInt64)        COMMENT '卖一量',
    ask_volume2   Nullable(UInt64)        COMMENT '卖二量',
    ask_volume3   Nullable(UInt64)        COMMENT '卖三量',
    ask_volume4   Nullable(UInt64)        COMMENT '卖四量',
    ask_volume5   Nullable(UInt64)        COMMENT '卖五量',
    quality_flag  UInt8          DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts     DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳(#ARCH-CH-025)',
    INDEX idx_ts timestamp TYPE minmax GRANULARITY 1,
    INDEX idx_symbol symbol TYPE set(10000) GRANULARITY 4,
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (market_type, symbol, trade_date, timestamp, price)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "tick_depth_5"
DATABASE = "c1_market"
CATEGORY_ID = "market_tick_depth_5"
CALC_MODE = "replay"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(market_type, symbol, trade_date, timestamp, price)"

# 列清单（INSERT 时显式指定，排除 DEFAULT/MATERIALIZED 列由 CH 自动填充）
# P0-1 双时间戳沿用：recorded_time 显式传入本地接收时间
TICK_DEPTH_COLUMNS = (
    "trade_date, timestamp, recorded_time, symbol, market_type, price, "
    "volume, amount, data_source, "
    "bid_price1, bid_price2, bid_price3, bid_price4, bid_price5, "
    "ask_price1, ask_price2, ask_price3, ask_price4, ask_price5, "
    "bid_volume1, bid_volume2, bid_volume3, bid_volume4, bid_volume5, "
    "ask_volume1, ask_volume2, ask_volume3, ask_volume4, ask_volume5, "
    "quality_flag"
)
INSERT_COLUMNS = f"({TICK_DEPTH_COLUMNS})"
