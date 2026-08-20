# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_hk_connect_flow
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.c1_market_writer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] hk_connect_flow 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""hk_connect_flow 表 DDL-as-Code（category_id: market_hk_connect_flow, calc_mode: lazy）。

本文件是 c1_market.hk_connect_flow 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

来源：由 .runtime/_gen_truth_sources.py 从 ClickHouse system.tables/system.columns
反向生成（机构升级 DDL 真源回写，#ARCH-CH-025 Schema 真源体系收口）。

列清单：
#   trade_date: Date
#   channel: LowCardinality(String)
#   net_buy_amount: Decimal(18, 2)
#   buy_amount: Decimal(18, 2)
#   sell_amount: Decimal(18, 2)
#   cumulative_net_buy: Decimal(18, 2)
#   daily_inflow: Decimal(18, 2)
#   daily_balance: Decimal(18, 2)
#   holding_market_value: Decimal(18, 2)
#   data_source: LowCardinality(String)
#   ingest_ts: DateTime64(3, 'UTC')
"""

from __future__ import annotations

# category_id: market_hk_connect_flow
# calc_mode: lazy

MARKET_HK_CONNECT_FLOW_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.hk_connect_flow
(
    trade_date               Date,
    channel                  LowCardinality(String),
    net_buy_amount           Decimal(18, 2),
    buy_amount               Decimal(18, 2),
    sell_amount              Decimal(18, 2),
    cumulative_net_buy       Decimal(18, 2),
    daily_inflow             Decimal(18, 2),
    daily_balance            Decimal(18, 2),
    holding_market_value     Decimal(18, 2),
    data_source              LowCardinality(String)  DEFAULT 'akshare',
    ingest_ts                DateTime64(3, 'UTC')  DEFAULT now()
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY trade_date, channel
"""

# 表元数据
TABLE_NAME = "hk_connect_flow"
DATABASE = "c1_market"
CATEGORY_ID = "market_hk_connect_flow"
CALC_MODE = "lazy"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "trade_date, channel"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
INSERT_COLUMNS = "(trade_date, channel, net_buy_amount, buy_amount, sell_amount, cumulative_net_buy, daily_inflow, daily_balance, holding_market_value)"
