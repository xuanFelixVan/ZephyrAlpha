# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_kline_sector_880
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.c1_market_writer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] kline_sector_880 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""kline_sector_880 表 DDL-as-Code（category_id: market_kline_sector_880, calc_mode: lazy）。

本文件是 c1_market.kline_sector_880 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

来源：由 .runtime/_gen_truth_sources.py 从 ClickHouse system.tables/system.columns
反向生成（机构升级 DDL 真源回写，#ARCH-CH-025 Schema 真源体系收口）。

列清单：
#   period: LowCardinality(String)
#   trade_date: Date
#   timestamp: DateTime64(3, 'Asia/Shanghai')
#   sector_code: String
#   sector_name: String
#   open: Decimal(18, 4)
#   high: Decimal(18, 4)
#   low: Decimal(18, 4)
#   close: Decimal(18, 4)
#   volume: UInt64
#   amount: Decimal(18, 2)
#   forward_factor: Decimal(18, 8)
#   data_source: LowCardinality(String)
#   fetched_at: DateTime64(3, 'UTC')
#   ingest_ts: DateTime64(3, 'UTC')
"""

from __future__ import annotations

# category_id: market_kline_sector_880
# calc_mode: lazy

MARKET_KLINE_SECTOR_880_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.kline_sector_880
(
    period                   LowCardinality(String)  COMMENT '1d/1m/5m',
    trade_date               Date  COMMENT '交易日期',
    timestamp                DateTime64(3, 'Asia/Shanghai')  COMMENT 'K线时间戳（日K=00:00:00）',
    sector_code              String  COMMENT '880001.SH 格式',
    sector_name              String  COMMENT '板块名称',
    open                     Decimal(18, 4)  COMMENT '开盘价',
    high                     Decimal(18, 4)  COMMENT '最高价',
    low                      Decimal(18, 4)  COMMENT '最低价',
    close                    Decimal(18, 4)  COMMENT '收盘价',
    volume                   UInt64  COMMENT '成交量',
    amount                   Decimal(18, 2)  COMMENT '成交额',
    forward_factor           Decimal(18, 8)  COMMENT '前复权因子（默认1.0）',
    data_source              LowCardinality(String)  DEFAULT 'tqcenter',
    fetched_at               DateTime64(3, 'UTC')  DEFAULT now(),
    ingest_ts                DateTime64(3, 'UTC')  DEFAULT now()
)
ENGINE = ReplacingMergeTree(fetched_at)
PARTITION BY (period, toYYYYMM(trade_date))
ORDER BY period, sector_code, timestamp
"""

# 表元数据
TABLE_NAME = "kline_sector_880"
DATABASE = "c1_market"
CATEGORY_ID = "market_kline_sector_880"
CALC_MODE = "lazy"
ENGINE = "ReplacingMergeTree(fetched_at)"
PARTITION_KEY = "(period, toYYYYMM(trade_date))"
ORDER_BY = "period, sector_code, timestamp"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
INSERT_COLUMNS = (
    "(period, trade_date, timestamp, sector_code, sector_name, open, high, low, close, volume, amount, forward_factor)"
)
