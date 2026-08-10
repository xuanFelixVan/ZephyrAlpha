# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.market_ipo_schedule
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] ipo_schedule 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""ipo_schedule（新股申购+上市日历）DDL-as-Code（category_id: market_ipo_schedule）.

A 股"特殊日子"数据资产——新股申购与上市日历（2026-08-10 新增）。
每只新股一行，记录申购日（打新冻结资金日）与上市日（炒新资金分流日）。
打新期间冻结资金吸筹效应、上市日资金分流，均是短期流动性扰动因素。

与 stock_list（含 list_date 上市日）的区别：
    - stock_list 是全市场股票主表，list_date 仅作为基础属性
    - ipo_schedule 聚焦"新股申购+上市事件"，含发行价/发行PE/募集资金/中签率等打新专属字段

引擎选型：
    ReplacingMergeTree（按 ipo_date+symbol 去重）。
    PARTITION BY toYYYYMM(ipo_date)——按申购日期月分区。
    ORDER BY (ipo_date, symbol)——按申购日点查友好。
"""

from __future__ import annotations

# category_id: market_ipo_schedule
# calc_mode: preload

IPO_SCHEDULE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.ipo_schedule
(
    ipo_date      Date                       COMMENT '申购日期',
    listing_date  Nullable(Date)             COMMENT '上市日期',
    symbol        String                     COMMENT '新股代码',
    name          String                     COMMENT '新股名称',
    issue_price   Nullable(Decimal(18, 4))   COMMENT '发行价(元)',
    issue_pe      Nullable(Decimal(18, 4))   COMMENT '发行市盈率',
    raise_amount  Nullable(Decimal(18, 2))   COMMENT '募集资金(元)',
    online_cap    Nullable(Decimal(10, 6))   COMMENT '网上中签率(%)',
    board         LowCardinality(String)     COMMENT '板块(主板/科创/创业/北交)',
    data_source   LowCardinality(String)     DEFAULT 'akshare' COMMENT '数据来源',
    ingest_ts     DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol,'.')>0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(ipo_date)
ORDER BY (ipo_date, symbol)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "ipo_schedule"
DATABASE = "c1_market"
CATEGORY_ID = "market_ipo_schedule"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(ipo_date)"
ORDER_BY = "(ipo_date, symbol)"

INSERT_COLUMNS = (
    "(ipo_date, listing_date, symbol, name, issue_price, issue_pe, raise_amount, online_cap, board, data_source)"
)
