# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c3_fundamental_clickhouse.md
# [MODULE] schemas.categories.fundamental_share_change
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_fundamental_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] share_change 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->verify_schema_truth.py 报漂移+apply_fundamental_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/verify_schema_truth.py --table share_change
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""share_change（股本变动）DDL-as-Code（category_id: fundamental_share_change）。

本文件是 c3_fundamental.share_change 表结构的唯一真源。

真源回写（#ARCH-CH-025，Wave 1，2026-07-25）：P0-8 DB 层已迁移 ReplacingMergeTree，本文件补齐真源。

引擎选型：
    ReplacingMergeTree（无版本列）。
    PARTITION BY toYYYYMM(announce_date)——按公告日期月分区。
    ORDER BY (symbol, announce_date)——单标的多变动点查友好。
"""

from __future__ import annotations

# category_id: fundamental_share_change
# calc_mode: preload

SHARE_CHANGE_DDL = """
CREATE TABLE IF NOT EXISTS c3_fundamental.share_change
(
    symbol            String                       COMMENT '证券代码',
    announce_date     Date                         COMMENT '公告日期',
    change_type       String                       COMMENT '变动类型',
    change_amount     Nullable(Float64)            COMMENT '变动数量',
    total_shares_after Nullable(Float64)           COMMENT '变动后总股本',
    data_source       LowCardinality(String) DEFAULT 'akshare' COMMENT '数据来源',
    ingest_ts         DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol,'.')>0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(announce_date)
ORDER BY (symbol, announce_date)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "share_change"
DATABASE = "c3_fundamental"
CATEGORY_ID = "fundamental_share_change"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(announce_date)"
ORDER_BY = "(symbol, announce_date)"

INSERT_COLUMNS = "(symbol, announce_date, change_type, change_amount, total_shares_after, data_source)"
