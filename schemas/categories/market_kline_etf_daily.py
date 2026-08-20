# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_kline_etf_daily
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.c1_market_writer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] kline_etf_daily 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""kline_etf_daily 表 DDL-as-Code（category_id: market_kline_etf_daily, calc_mode: preload）。

本文件是 c1_market.kline_etf_daily 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

背景：
    ETF 日线补建（2026-07-29）。原 ETF 仅有 1/5/15/30/60 分钟线，缺日线表。
    provider（miniqmt_provider.py）的 fetch_kline 日线分支（period=="1d"）已实现，
    通过 _KLINE_CAPABILITIES["kline_etf_daily"]=("1d","沪深ETF") 激活。
    字段对齐 provider 日线输出 8 列 (trade_date, symbol, open, high, low, close,
    volume, amount)，其余列由 DEFAULT 自动填充。

列清单：
#   trade_date: Date
#   symbol: String
#   open: Decimal(18, 4)
#   high: Decimal(18, 4)
#   low: Decimal(18, 4)
#   close: Decimal(18, 4)
#   volume: UInt64
#   amount: Decimal(18, 2)
#   pct_change: Decimal(18, 4) DEFAULT 0
#   amplitude: Decimal(18, 4) DEFAULT 0
#   data_source: LowCardinality(String) DEFAULT 'miniqmt'
#   ingest_ts: DateTime64(3, 'UTC') DEFAULT now()
"""

from __future__ import annotations

# category_id: market_kline_etf_daily
# calc_mode: preload

MARKET_KLINE_ETF_DAILY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.kline_etf_daily
(
    trade_date               Date,
    symbol                   String,
    open                     Decimal(18, 4),
    high                     Decimal(18, 4),
    low                      Decimal(18, 4),
    close                    Decimal(18, 4),
    volume                   UInt64,
    amount                   Decimal(18, 2),
    pct_change               Decimal(18, 4)  DEFAULT 0,
    amplitude                Decimal(18, 4)  DEFAULT 0,
    data_source              LowCardinality(String)  DEFAULT 'miniqmt',
    ingest_ts                DateTime64(3, 'UTC')  DEFAULT now(),
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
"""

# 表元数据
TABLE_NAME = "kline_etf_daily"
DATABASE = "c1_market"
CATEGORY_ID = "market_kline_etf_daily"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(symbol, trade_date)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
# 严格对齐 provider 日线分支输出（OHLC 顺序），8 列
INSERT_COLUMNS = "(trade_date, symbol, open, high, low, close, volume, amount)"
