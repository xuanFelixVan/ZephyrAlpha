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
   - 5 字段完全相同的行（14 字段全相同的重复记录）仍会被 ReplacingMergeTree 合并
2. PARTITION BY toYYYYMM(trade_date) 月级分区
   - 日级分区(toYYYYMMDD)在 93 亿行规模下分区数过多（>8000），增加 merge 开销
   - 月级分区约 45 个分区，兼顾分区裁剪性能与 merge 效率
3. ReplacingMergeTree（无版本列）
   - 无 ingest_ts 版本列，重复行按插入顺序保留最后一条
   - 数据源重复导入产生的 5 字段完全重复行被自动合并（正确行为）
4. direction 列 LowCardinality(String)
   - A 股逐笔成交方向（买/卖/中性），index 数据无方向填空串
5. bid/ask 价格量 Nullable
   - 逐笔成交无买卖盘信息，index 数据填 NULL
"""
from __future__ import annotations

# category_id: market_tick
# calc_mode: replay（回测时逐笔回放，保证=实盘）

TICK_DATA_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.tick_data
(
    trade_date   Date                    COMMENT '交易日期',
    timestamp    DateTime                COMMENT '时间戳(3秒粒度)',
    symbol       String                  COMMENT '证券代码',
    market_type  LowCardinality(String)  COMMENT '市场类型(A_share/futures/index)',
    price        Decimal(18,4)           COMMENT '成交价',
    volume       UInt64                  COMMENT '成交量(股)',
    amount       Decimal(18,2)           COMMENT '成交额(元)',
    direction    LowCardinality(String) DEFAULT '' COMMENT '买卖方向(买/卖/中性)',
    data_source  LowCardinality(String) DEFAULT 'bdpan' COMMENT '数据来源',
    bid_price    Nullable(Decimal(18,4)) COMMENT '买一价',
    ask_price    Nullable(Decimal(18,4)) COMMENT '卖一价',
    bid_volume   Nullable(UInt64)        COMMENT '买一量',
    ask_volume   Nullable(UInt64)        COMMENT '卖一量',
    quality_flag UInt8          DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)'
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
INSERT_COLUMNS = (
    "(trade_date, timestamp, symbol, market_type, price, volume, amount, "
    "direction, data_source, bid_price, ask_price, bid_volume, ask_volume, "
    "quality_flag)"
)
