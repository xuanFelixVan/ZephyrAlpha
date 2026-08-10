# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.market_margin_target_adjustment
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] margin_target_adjustment 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""margin_target_adjustment（两融标的调整事件）DDL-as-Code（category_id: market_margin_target_adjustment）.

A 股"特殊日子"数据资产——融资融券标的纳入/剔除事件（2026-08-10 新增）。
沪深交易所定期（通常每季度）调整融资融券标的名单，标的变动引发杠杆资金被迫加减仓。

与 margin_trading（融资融券余额数据）的区别：
    - margin_trading 记录"每日余额数据"（融资买入额/融券卖出量等）
    - margin_target_adjustment 记录"标的名单调整事件"（某只股票被纳入或剔除两融标的）

采集策略：
    akshare stock_margin_underlying_info_szse/sse 返回"当前标的列表"。
    Provider 每次拉取当前列表，与上次快照 diff，新增=inclusion，消失=exclusion。
    首次运行无基线，全部记为 inclusion（基线建立），后续运行 diff 出真实调整。

引擎选型：
    ReplacingMergeTree（按 effective_date+symbol+margin_type+action 去重）。
    PARTITION BY toYYYYMM(effective_date)——按生效日期月分区。
    ORDER BY (effective_date, symbol)——按日期点查友好。
"""

from __future__ import annotations

# category_id: market_margin_target_adjustment
# calc_mode: preload

MARGIN_TARGET_ADJUSTMENT_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.margin_target_adjustment
(
    announcement_date  Date                       COMMENT '公告日期',
    effective_date     Date                       COMMENT '生效日期',
    symbol             String                     COMMENT '证券代码',
    action             LowCardinality(String)     COMMENT 'inclusion/exclusion(纳入/剔除)',
    margin_type        LowCardinality(String)     COMMENT 'financing/securities/both(融资/融券/两者)',
    data_source        LowCardinality(String)     DEFAULT 'akshare' COMMENT '数据来源',
    ingest_ts          DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol,'.')>0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(effective_date)
ORDER BY (effective_date, symbol)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "margin_target_adjustment"
DATABASE = "c1_market"
CATEGORY_ID = "market_margin_target_adjustment"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(effective_date)"
ORDER_BY = "(effective_date, symbol)"

INSERT_COLUMNS = "(announcement_date, effective_date, symbol, action, margin_type, data_source)"
