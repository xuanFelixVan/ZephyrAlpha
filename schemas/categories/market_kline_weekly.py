# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_kline_weekly
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.c1_market_writer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] kline_weekly 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""kline_weekly 表 DDL-as-Code（category_id: market_kline_weekly, calc_mode: lazy）。

本文件是 c1_market.kline_weekly 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

来源：由 .runtime/_gen_truth_sources.py 从 ClickHouse system.tables/system.columns
反向生成（机构升级 DDL 真源回写，#ARCH-CH-025 Schema 真源体系收口）。

列清单：
#   trade_date: Date
#   symbol: String
#   open: Decimal(18, 4)
#   close: Decimal(18, 4)
#   high: Decimal(18, 4)
#   low: Decimal(18, 4)
#   volume: UInt64
#   amount: Decimal(18, 2)
#   amplitude: Decimal(18, 4)
#   pct_change: Decimal(18, 4)
#   change: Decimal(18, 4)
#   turnover: Decimal(18, 4)
#   data_source: LowCardinality(String)
#   ingest_ts: DateTime64(3, 'UTC')
"""

from __future__ import annotations

# category_id: market_kline_weekly
# calc_mode: lazy

MARKET_KLINE_WEEKLY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.kline_weekly
(
    trade_date               Date  COMMENT '周线日期(周末)',
    symbol                   String  COMMENT '证券代码(6位数字)',
    open                     Decimal(18, 4)  COMMENT '开盘价(前复权)',
    close                    Decimal(18, 4)  COMMENT '收盘价(前复权)',
    high                     Decimal(18, 4)  COMMENT '最高价(前复权)',
    low                      Decimal(18, 4)  COMMENT '最低价(前复权)',
    volume                   UInt64  COMMENT '成交量(股)',
    amount                   Decimal(18, 2)  COMMENT '成交额(元)',
    amplitude                Decimal(18, 4)  COMMENT '振幅(%)',
    pct_change               Decimal(18, 4)  COMMENT '涨跌幅(%)',
    change                   Decimal(18, 4)  COMMENT '涨跌额(元)',
    turnover                 Decimal(18, 4)  COMMENT '换手率(%)',
    data_source              LowCardinality(String)  DEFAULT 'local_qfq'  COMMENT '数据来源',
    ingest_ts                DateTime64(3, 'UTC')  DEFAULT now(),
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY symbol, trade_date
"""

# 表元数据
TABLE_NAME = "kline_weekly"
DATABASE = "c1_market"
CATEGORY_ID = "market_kline_weekly"
CALC_MODE = "lazy"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "symbol, trade_date"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
INSERT_COLUMNS = "(trade_date, symbol, open, close, high, low, volume, amount, amplitude, pct_change, change, turnover)"
