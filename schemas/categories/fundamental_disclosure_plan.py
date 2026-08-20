# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c3_fundamental_clickhouse.md
# [MODULE] schemas.categories.fundamental_disclosure_plan
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_fundamental_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] disclosure_plan 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->verify_schema_truth.py 报漂移+apply_fundamental_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/verify_schema_truth.py --table disclosure_plan
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""disclosure_plan（披露计划）DDL-as-Code（category_id: fundamental_disclosure_plan, calc_mode: preload）。

本文件是 c3_fundamental.disclosure_plan 表结构的唯一真源（DDL-as-Code 模式）。

真源回写（#ARCH-CH-025 Schema 真源体系收口，Wave 1，2026-07-25）：
    P0-8 已在 DB 层迁移至 ReplacingMergeTree（原裸 MergeTree 走写前 DELETE 反模式），
    本文件补齐真源断层。

引擎选型：
    ReplacingMergeTree（无版本列）。
    PARTITION BY toYYYYMM(report_period)——按报告期月分区。
    ORDER BY (symbol, report_period)——单标的多报告期点查友好。
"""

from __future__ import annotations

# category_id: fundamental_disclosure_plan
# calc_mode: preload

DISCLOSURE_PLAN_DDL = """
CREATE TABLE IF NOT EXISTS c3_fundamental.disclosure_plan
(
    symbol          String          COMMENT '6位代码',
    report_period   Date            COMMENT '报告期',
    announce_date   Date            COMMENT '公告日期',
    scheduled_date  Nullable(Date)  COMMENT '预约披露日期',
    actual_date     Nullable(Date)  COMMENT '实际披露日期',
    data_source     String          COMMENT '数据来源',
    quality_flag    UInt8 DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts       DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol,'.')>0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(report_period)
ORDER BY (symbol, report_period)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "disclosure_plan"
DATABASE = "c3_fundamental"
CATEGORY_ID = "fundamental_disclosure_plan"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(report_period)"
ORDER_BY = "(symbol, report_period)"

INSERT_COLUMNS = "(symbol, report_period, announce_date, scheduled_date, actual_date, data_source, quality_flag)"
