# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_us_index
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.c1_market_writer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] us_index 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""us_index 表 DDL-as-Code（category_id: market_us_index, calc_mode: lazy）。

本文件是 c1_market.us_index 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

来源：由 .runtime/_gen_truth_sources.py 从 ClickHouse system.tables/system.columns
反向生成（机构升级 DDL 真源回写，#ARCH-CH-025 Schema 真源体系收口）。

列清单：
#   trade_date: Date
#   symbol: String
#   open: Decimal(18, 4)
#   high: Decimal(18, 4)
#   low: Decimal(18, 4)
#   close: Decimal(18, 4)
#   volume: UInt64
#   data_source: LowCardinality(String)
#   ingest_ts: DateTime64(3, 'UTC')
"""

from __future__ import annotations

# category_id: market_us_index
# calc_mode: lazy

MARKET_US_INDEX_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.us_index
(
    trade_date               Date,
    symbol                   String,
    open                     Decimal(18, 4),
    high                     Decimal(18, 4),
    low                      Decimal(18, 4),
    close                    Decimal(18, 4),
    volume                   UInt64,
    data_source              LowCardinality(String)  DEFAULT 'tickflow',
    ingest_ts                DateTime64(3, 'UTC')  DEFAULT now(),
    exchange LowCardinality(String) MATERIALIZED 'US' COMMENT '交易所码(市场隐含TRAE-082)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY symbol, trade_date
"""

# 表元数据
TABLE_NAME = "us_index"
DATABASE = "c1_market"
CATEGORY_ID = "market_us_index"
CALC_MODE = "lazy"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "symbol, trade_date"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
INSERT_COLUMNS = "(trade_date, symbol, open, high, low, close, volume)"
