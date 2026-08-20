# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_kline_sector_intraday
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.c1_market_writer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] kline_sector_intraday 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""kline_sector_intraday 表 DDL-as-Code（category_id: market_kline_sector_intraday, calc_mode: lazy）。

本文件是 c1_market.kline_sector_intraday 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

来源：由 .runtime/_gen_truth_sources.py 从 ClickHouse system.tables/system.columns
反向生成（机构升级 DDL 真源回写，#ARCH-CH-025 Schema 真源体系收口）。

列清单：
#   trade_date: DateTime64(3, 'Asia/Shanghai')
#   code: String
#   period: LowCardinality(String)
#   open: Decimal(18, 4)
#   high: Decimal(18, 4)
#   low: Decimal(18, 4)
#   close: Decimal(18, 4)
#   volume: UInt64
#   amount: Decimal(18, 2)
#   data_source: LowCardinality(String)
#   ingest_ts: DateTime64(3, 'UTC')
"""

from __future__ import annotations

# category_id: market_kline_sector_intraday
# calc_mode: lazy

MARKET_KLINE_SECTOR_INTRADAY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.kline_sector_intraday
(
    trade_date               DateTime64(3, 'Asia/Shanghai')  COMMENT '分钟K线时间戳',
    code                     String  COMMENT '板块代码 880xxx.SH',
    period                   LowCardinality(String)  COMMENT 'K线周期 1m/5m/15m/30m/60m',
    open                     Decimal(18, 4),
    high                     Decimal(18, 4),
    low                      Decimal(18, 4),
    close                    Decimal(18, 4),
    volume                   UInt64,
    amount                   Decimal(18, 2),
    data_source              LowCardinality(String)  DEFAULT 'tdx',
    ingest_ts                DateTime64(3, 'UTC')  DEFAULT now()
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMMDD(trade_date)
ORDER BY code, period, trade_date
"""

# 表元数据
TABLE_NAME = "kline_sector_intraday"
DATABASE = "c1_market"
CATEGORY_ID = "market_kline_sector_intraday"
CALC_MODE = "lazy"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMMDD(trade_date)"
ORDER_BY = "code, period, trade_date"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
INSERT_COLUMNS = "(trade_date, code, period, open, high, low, close, volume, amount)"
