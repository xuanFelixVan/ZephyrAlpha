# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.market_msci_adjustment
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] msci_adjustment 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""msci_adjustment（MSCI/富时调整事件）DDL-as-Code（category_id: market_msci_adjustment）.

A 股"特殊日子"数据资产——MSCI/富时罗素指数调整事件（2026-08-10 新增，表结构预留）。
MSCI 季度审议（通常2/5/8/11月）与富时罗素半年度审议引发外资被动调仓，
是 A 股外资流入/流出的重要前向特征。

数据源现状：
    akshare/tushare 均无 MSCI/富时调整的直接接口。
    本批次只建立表结构，采集任务 disabled。后续路径：
      1) 爬虫 MSCI 官网 quarterly review 公告
      2) 接入第三方数据源（如 Wind/Choice 等商业数据源的 MSCI 调整专题）
      3) 手工录入历次调整事件
    数据填充前 data_source='manual'，填充后可改为对应数据源标识。

引擎选型：
    ReplacingMergeTree（按 index_provider+effective_date+symbol+action 去重）。
    PARTITION BY toYYYYMM(effective_date)——按生效日期月分区。
    ORDER BY (index_provider, effective_date, symbol)——按提供商+日期点查友好。
"""

from __future__ import annotations

# category_id: market_msci_adjustment
# calc_mode: preload

MSCI_ADJUSTMENT_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.msci_adjustment
(
    announcement_date  Date                       COMMENT '公告日期',
    effective_date     Date                       COMMENT '生效日期',
    index_provider     LowCardinality(String)     COMMENT '指数提供商(MSCI/FTSE)',
    symbol             String                     COMMENT '成分股代码',
    action             LowCardinality(String)     COMMENT 'inclusion/exclusion(纳入/剔除)',
    weight             Nullable(Decimal(10, 6))   COMMENT '调整后权重(%)',
    data_source        LowCardinality(String)     DEFAULT 'manual' COMMENT '数据来源(manual=手工录入,待数据源接入)',
    ingest_ts          DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol,'.')>0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(effective_date)
ORDER BY (index_provider, effective_date, symbol)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "msci_adjustment"
DATABASE = "c1_market"
CATEGORY_ID = "market_msci_adjustment"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(effective_date)"
ORDER_BY = "(index_provider, effective_date, symbol)"

INSERT_COLUMNS = "(announcement_date, effective_date, index_provider, symbol, action, weight, data_source)"
