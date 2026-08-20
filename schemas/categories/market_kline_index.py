# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_kline_index
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.c1_market_writer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] kline_index 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""kline_index 表 DDL-as-Code（category_id: market_kline_index, calc_mode: lazy）。

本文件是 c1_market.kline_index 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

来源：由 .runtime/_gen_truth_sources.py 从 ClickHouse system.tables/system.columns
反向生成（机构升级 DDL 真源回写，#ARCH-CH-025 Schema 真源体系收口）。

列清单：
#   trade_date: Date
#   symbol: String
#   name: String
#   open: Decimal(18, 4)
#   high: Decimal(18, 4)
#   low: Decimal(18, 4)
#   close: Decimal(18, 4)
#   volume: UInt64
#   amount: Decimal(18, 2)
#   advance_count: UInt32
#   decline_count: UInt32
#   data_source: String
#   quality_flag: UInt8
#   ingest_ts: DateTime64(3, 'UTC')
"""

from __future__ import annotations

# category_id: market_kline_index
# calc_mode: lazy

MARKET_KLINE_INDEX_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.kline_index
(
    trade_date               Date,
    symbol                   String  COMMENT '指数代码',
    name                     String  COMMENT '指数名称',
    open                     Decimal(18, 4),
    high                     Decimal(18, 4),
    low                      Decimal(18, 4),
    close                    Decimal(18, 4),
    volume                   UInt64  DEFAULT 0,
    amount                   Decimal(18, 2)  DEFAULT 0,
    advance_count            UInt32  DEFAULT 0  COMMENT '上涨家数',
    decline_count            UInt32  DEFAULT 0  COMMENT '下跌家数',
    data_source              String,
    quality_flag             UInt8  DEFAULT 1,
    ingest_ts                DateTime64(3, 'UTC')  DEFAULT now(),
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('000', '880', '930', '931', '932'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('399'), 'SZ', '') COMMENT '交易所码(TRAE-082 指数专用MATERIALIZED派生,000001.SH上证指数)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(trade_date)
ORDER BY symbol, trade_date
"""

# 表元数据
TABLE_NAME = "kline_index"
DATABASE = "c1_market"
CATEGORY_ID = "market_kline_index"
CALC_MODE = "lazy"
ENGINE = "ReplacingMergeTree(ingest_ts)"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "symbol, trade_date"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
INSERT_COLUMNS = "(trade_date, symbol, name, open, high, low, close, data_source)"
