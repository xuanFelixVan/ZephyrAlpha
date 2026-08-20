# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_dragon_tiger_seat
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.c1_market_writer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] dragon_tiger_seat 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""dragon_tiger_seat 表 DDL-as-Code（category_id: market_dragon_tiger_seat, calc_mode: lazy）。

龙虎榜席位明细：存储个股龙虎榜 Top5 买入/卖出营业部席位买卖额明细。
数据源：akshare stock_lhb_stock_detail_em（买入/卖出 Top5 合并去重）。
与 dragon_tiger（汇总）一对多：一只股票一日 → 多个席位行。

列清单：
#   trade_date: Date
#   symbol: String
#   seat_name: String 营业部名称(机构专用/深股通专用/xx证券xx营业部)
#   buy_amount: Decimal(18, 2) 买入金额
#   sell_amount: Decimal(18, 2) 卖出金额
#   net_amount: Decimal(18, 2) 净额
#   buy_rank: Nullable(UInt8) 买入榜排名(1-5)
#   sell_rank: Nullable(UInt8) 卖出榜排名(1-5)
#   seat_type: LowCardinality(String) 席位类型(institution/broker/connect)
#   reason: String 上榜原因
#   data_source: LowCardinality(String)
#   ingest_ts: DateTime64(3, 'UTC')
"""

from __future__ import annotations

# category_id: market_dragon_tiger_seat
# calc_mode: lazy

MARKET_DRAGON_TIGER_SEAT_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.dragon_tiger_seat
(
    trade_date               Date,
    symbol                   String,
    seat_name                String,
    buy_amount               Decimal(18, 2),
    sell_amount              Decimal(18, 2),
    net_amount               Decimal(18, 2),
    buy_rank                 Nullable(UInt8),
    sell_rank                Nullable(UInt8),
    seat_type                LowCardinality(String)  DEFAULT 'broker' COMMENT '席位类型(institution/broker/connect)',
    reason                   String,
    data_source              LowCardinality(String)  DEFAULT 'akshare',
    ingest_ts                DateTime64(3, 'UTC')  DEFAULT now(),
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, symbol, seat_name)
"""

# 表元数据
TABLE_NAME = "dragon_tiger_seat"
DATABASE = "c1_market"
CATEGORY_ID = "market_dragon_tiger_seat"
CALC_MODE = "lazy"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "trade_date, symbol, seat_name"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT/MATERIALIZED 列由 CH 自动填充）
INSERT_COLUMNS = (
    "(trade_date, symbol, seat_name, buy_amount, sell_amount, net_amount, buy_rank, sell_rank, seat_type, reason)"
)
