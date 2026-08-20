# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c3_fundamental_clickhouse.md
# [MODULE] schemas.categories.fundamental_industry_class_suppl
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_fundamental_tables_ddl; zephyr.data.implementations.tushare_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] industry_class_suppl 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->verify_schema_truth.py 报漂移+apply_fundamental_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/verify_schema_truth.py --table industry_class_suppl
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""industry_class_suppl（补充行业分类）DDL-as-Code（category_id: fundamental_industry_class_suppl）。

本文件是 c3_fundamental.industry_class_suppl 表结构的唯一真源。

真源回写（#ARCH-CH-025，Wave 1，2026-07-25）：P0-8 DB 层已迁移 ReplacingMergeTree，本文件补齐真源。

引擎选型：
    ReplacingMergeTree（无版本列）。
    无 PARTITION BY（表规模小，单标的多版本点查为主，月分区无收益）。
    ORDER BY (symbol)——按标的点查。

SCD-2 时点版本（#ARCH-CH-021 P0-6，缓变维表）：
    valid_from/valid_to/updated_at 三列支持时点查询——回测到历史日期时取该日有效的行业分类，
    消除"用当前行业分类回测历史"的前视偏差。valid_from DEFAULT today()，valid_to NULL=当前有效。
"""

from __future__ import annotations

# category_id: fundamental_industry_class_suppl
# calc_mode: preload

INDUSTRY_CLASS_SUPPL_DDL = """
CREATE TABLE IF NOT EXISTS c3_fundamental.industry_class_suppl
(
    symbol          String                       COMMENT '证券代码',
    industry_sw     String                       COMMENT '申万行业分类',
    industry_zsi    String                       COMMENT '中证行业分类',
    industry_level  UInt8 DEFAULT 0              COMMENT '行业等级',
    data_source     LowCardinality(String) DEFAULT 'tushare' COMMENT '数据来源',
    valid_from      Date DEFAULT today()         COMMENT 'SCD-2生效起始日',
    valid_to        Nullable(Date)               COMMENT 'SCD-2生效终止日(NULL=当前有效)',
    updated_at      DateTime64(3, 'UTC') DEFAULT now() COMMENT '记录更新时间',
    ingest_ts       DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol,'.')>0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
ORDER BY (symbol)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "industry_class_suppl"
DATABASE = "c3_fundamental"
CATEGORY_ID = "fundamental_industry_class_suppl"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = ""
ORDER_BY = "(symbol)"

INSERT_COLUMNS = "(symbol, industry_sw, industry_zsi, industry_level, data_source, valid_from, valid_to, updated_at)"
