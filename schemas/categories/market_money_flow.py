# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_money_flow
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.c1_market_writer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] money_flow 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""money_flow 表 DDL-as-Code（category_id: market_money_flow, calc_mode: lazy）。

本文件是 c1_market.money_flow 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

来源：由 .runtime/_gen_truth_sources.py 从 ClickHouse system.tables/system.columns
反向生成（机构升级 DDL 真源回写，#ARCH-CH-025 Schema 真源体系收口）。

列清单：
#   trade_date: Date
#   symbol: String
#   close: Decimal(18, 4)
#   pct_change: Decimal(18, 4)
#   main_net_inflow: Decimal(18, 2)
#   main_net_inflow_pct: Decimal(18, 4)
#   super_large_net_inflow: Decimal(18, 2)
#   super_large_net_inflow_pct: Decimal(18, 4)
#   large_net_inflow: Decimal(18, 2)
#   large_net_inflow_pct: Decimal(18, 4)
#   medium_net_inflow: Decimal(18, 2)
#   medium_net_inflow_pct: Decimal(18, 4)
#   small_net_inflow: Decimal(18, 2)
#   small_net_inflow_pct: Decimal(18, 4)
#   data_source: LowCardinality(String)
#   ingest_ts: DateTime64(3, 'UTC')
"""

from __future__ import annotations

# category_id: market_money_flow
# calc_mode: lazy

MARKET_MONEY_FLOW_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.money_flow
(
    trade_date               Date  COMMENT '交易日期',
    symbol                   String  COMMENT '证券代码(sh/sz前缀+6位)',
    close                    Decimal(18, 4)  COMMENT '收盘价',
    pct_change               Decimal(18, 4)  COMMENT '涨跌幅(%)',
    main_net_inflow          Decimal(18, 2)  COMMENT '主力净流入-净额(万元)',
    main_net_inflow_pct      Decimal(18, 4)  COMMENT '主力净流入-净占比(%)',
    super_large_net_inflow   Decimal(18, 2)  COMMENT '超大单净流入-净额(万元)',
    super_large_net_inflow_pct Decimal(18, 4)  COMMENT '超大单净流入-净占比(%)',
    large_net_inflow         Decimal(18, 2)  COMMENT '大单净流入-净额(万元)',
    large_net_inflow_pct     Decimal(18, 4)  COMMENT '大单净流入-净占比(%)',
    medium_net_inflow        Decimal(18, 2)  COMMENT '中单净流入-净额(万元)',
    medium_net_inflow_pct    Decimal(18, 4)  COMMENT '中单净流入-净占比(%)',
    small_net_inflow         Decimal(18, 2)  COMMENT '小单净流入-净额(万元)',
    small_net_inflow_pct     Decimal(18, 4)  COMMENT '小单净流入-净占比(%)',
    data_source              LowCardinality(String)  DEFAULT 'local_moneyflow'  COMMENT '数据来源',
    ingest_ts                DateTime64(3, 'UTC')  DEFAULT now(),
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY symbol, trade_date
"""

# 表元数据
TABLE_NAME = "money_flow"
DATABASE = "c1_market"
CATEGORY_ID = "market_money_flow"
CALC_MODE = "lazy"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "symbol, trade_date"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
INSERT_COLUMNS = "(trade_date, symbol, close, pct_change, main_net_inflow, main_net_inflow_pct, super_large_net_inflow, super_large_net_inflow_pct, large_net_inflow, large_net_inflow_pct, medium_net_inflow, medium_net_inflow_pct, small_net_inflow, small_net_inflow_pct)"
