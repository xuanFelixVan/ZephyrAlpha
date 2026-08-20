# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_tick
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_schema.py; zephyr.data.c1_market_writer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] tick_data 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [TTL] permanent
"""tick_data 表 DDL-as-Code（category_id: market_tick, calc_mode: replay）。

本文件是 c1_market.tick_data 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

设计决策（2026-07-16 表结构修复，裁定 #ARCH-CH-002）：
1. ORDER BY 5 字段 (market_type, symbol, trade_date, timestamp, price)
   - 源表 ORDER BY 4 字段 (market_type, symbol, trade_date, timestamp) 会合并
     4 字段相同但 price 不同的有效行（同一时刻不同价位的成交流水）
   - 新增 price 作为第 5 排序键，确保同一时间戳不同价位的成交不被合并
   - 5 字段完全相同的行（重复记录）仍会被 ReplacingMergeTree 合并
2. PARTITION BY toYYYYMM(trade_date) 月级分区
   - 日级分区(toYYYYMMDD)在 93 亿行规模下分区数过多（>8000），增加 merge 开销
   - 月级分区约 45 个分区，兼顾分区裁剪性能与 merge 效率
3. ReplacingMergeTree（无版本列）
   - 无 ingest_ts 版本列，重复行按插入顺序保留最后一条
   - 数据源重复导入产生的 5 字段完全重复行被自动合并（正确行为）
4. direction 列 LowCardinality(String)
   - A股3秒Tick方向（买/卖/中性），index 数据无方向填空串
5. bid/ask 价格量 Nullable
   - 3秒Tick无买卖盘信息，index 数据填 NULL
6. recorded_time 列（2026-07-22 新增，P0-1 双时间戳）
   - event_time=timestamp（上游市场时间），recorded_time=录制器本地接收时间
   - recorded_time - timestamp = 端到端延迟，用于回测延迟建模
   - DEFAULT now() 由 ClickHouse 自动填充，INSERT 显式传入本地时间
   - 不影响 ORDER BY（元数据级新增，O(1) 操作）
7. 数据跳过索引（audit 1.3/5.3 治本，#ARCH-CH-028，2026-07-23）
   - INDEX idx_ts timestamp TYPE minmax GRANULARITY 1: 时间戳范围裁剪
   - INDEX idx_symbol symbol TYPE set(10000) GRANULARITY 4: 单标的精确裁剪
   - 背景: ORDER BY 以 market_type 为前缀（#ARCH-CH-020 防跨市场去重事故），
     导致单标的查询无法使用主键前缀裁剪。set(10000) 索引在每个 granule 块
     （4×8192=32768 行）存储至多 10000 个 distinct symbol，支持精确点查裁剪。
8. 时区防线（audit A组 时区治理，#ARCH-CH-022，2026-07-24）
   - timestamp(业务墙钟) -> DateTime64(3, 'Asia/Shanghai')，迁移时数据偏移 -8h
   - recorded_time/ingest_ts(now() 真 UTC) -> DateTime64(3, 'UTC')，无偏移
   - 消除 UTC/北京时间混存导致的 8 小时算术偏差；迁移由 apply_timezone_migration.py 执行
"""

from __future__ import annotations

# category_id: market_tick
# calc_mode: replay（回测时逐条回放3秒Tick，保证=实盘）

TICK_DATA_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.tick_data
(
    trade_date    Date                    COMMENT '交易日期',
    timestamp     DateTime64(3, 'Asia/Shanghai') COMMENT '时间戳(3秒粒度)',
    recorded_time DateTime64(3, 'UTC')  DEFAULT now() COMMENT '录制器本地接收时间(用于延迟分析)',
    symbol        String                  COMMENT '证券代码',
    market_type   LowCardinality(String)  COMMENT '市场类型(A_share/futures/index)',
    price         Decimal(18,4)           COMMENT '成交价',
    volume        UInt64                  COMMENT '成交量(股)',
    amount        Decimal(18,2)           COMMENT '成交额(元)',
    direction     LowCardinality(String) DEFAULT '' COMMENT '买卖方向(买/卖/中性)',
    data_source   LowCardinality(String) DEFAULT 'bdpan' COMMENT '数据来源',
    bid_price     Nullable(Decimal(18,4)) COMMENT '买一价',
    ask_price     Nullable(Decimal(18,4)) COMMENT '卖一价',
    bid_volume    Nullable(UInt64)        COMMENT '买一量',
    ask_volume    Nullable(UInt64)        COMMENT '卖一量',
    quality_flag  UInt8          DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts     DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)',
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
TABLE_NAME = "tick_data"
DATABASE = "c1_market"
CATEGORY_ID = "market_tick"
CALC_MODE = "replay"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(market_type, symbol, trade_date, timestamp, price)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
# P0-1: 新增 recorded_time（显式传入本地接收时间，不依赖 CH DEFAULT now()）
INSERT_COLUMNS = (
    "(trade_date, timestamp, recorded_time, symbol, market_type, price, "
    "volume, amount, direction, data_source, bid_price, ask_price, "
    "bid_volume, ask_volume, quality_flag)"
)
