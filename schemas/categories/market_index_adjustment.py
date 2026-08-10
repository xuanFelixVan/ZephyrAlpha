# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.market_index_adjustment
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] index_adjustment 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""index_adjustment（指数成分股调整事件）DDL-as-Code（category_id: market_index_adjustment）.

A 股"特殊日子"数据资产——指数成分股纳入/剔除事件历史（2026-08-10 新增）。
每次指数定期调整（沪深300/中证500/中证1000等半年/年度调整）记录为每只股票一行事件。
被动指数基金强制调仓，引发资金流入/流出，是重要的前向特征。

与 index_constituent（当前成分快照）、index_weight（权重 SCD-2）的区别：
    - index_constituent / index_weight 记录"当前状态 / 历史权重快照"
    - index_adjustment 记录"调整事件"（某只股票在某次调整中被纳入或剔除）

引擎选型：
    ReplacingMergeTree（按 index_code+effective_date+symbol+action 去重）。
    PARTITION BY toYYYYMM(effective_date)——按生效日期月分区。
    ORDER BY (index_code, effective_date, symbol)——按指数+日期点查友好。
"""

from __future__ import annotations

# category_id: market_index_adjustment
# calc_mode: preload

INDEX_ADJUSTMENT_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.index_adjustment
(
    announcement_date  Date                       COMMENT '公告日期',
    effective_date     Date                       COMMENT '生效日期',
    index_code         String                     COMMENT '指数代码(000300.SH/000905.SH/000852.SH)',
    symbol             String                     COMMENT '成分股代码',
    action             LowCardinality(String)     COMMENT 'inclusion/exclusion(纳入/剔除)',
    weight             Nullable(Decimal(10, 6))   COMMENT '调整后权重(%)',
    data_source        LowCardinality(String)     DEFAULT 'akshare' COMMENT '数据来源',
    ingest_ts          DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol,'.')>0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(effective_date)
ORDER BY (index_code, effective_date, symbol)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "index_adjustment"
DATABASE = "c1_market"
CATEGORY_ID = "market_index_adjustment"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(effective_date)"
ORDER_BY = "(index_code, effective_date, symbol)"

INSERT_COLUMNS = "(announcement_date, effective_date, index_code, symbol, action, weight, data_source)"
