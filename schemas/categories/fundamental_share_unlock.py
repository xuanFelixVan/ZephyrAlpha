# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c3_fundamental_clickhouse.md
# [MODULE] schemas.categories.fundamental_share_unlock
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_fundamental_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] share_unlock 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->verify_schema_truth.py 报漂移+apply_fundamental_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/verify_schema_truth.py --table share_unlock
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""share_unlock（解除限售）DDL-as-Code（category_id: fundamental_share_unlock）。

本文件是 c3_fundamental.share_unlock 表结构的唯一真源。

真源回写（#ARCH-CH-025，Wave 1，2026-07-25）：P0-8 DB 层已迁移 ReplacingMergeTree，本文件补齐真源。

引擎选型：
    ReplacingMergeTree（无版本列）。
    PARTITION BY toYYYYMM(unlock_date)——按解禁日期月分区。
    ORDER BY (symbol, unlock_date)——单标的解禁点查友好。

注：shares/amount 为 Decimal(18,2)、ratio 为 Decimal(18,4)——本表已采用 Decimal 精度
   （早于 #ARCH-CH-026 财务三表迁移，独立落地）。
"""

from __future__ import annotations

# category_id: fundamental_share_unlock
# calc_mode: preload

SHARE_UNLOCK_DDL = """
CREATE TABLE IF NOT EXISTS c3_fundamental.share_unlock
(
    symbol       String                       COMMENT '证券代码',
    unlock_date  Date                         COMMENT '解除限售日期',
    shares       Decimal(18, 2)               COMMENT '解除限售数量',
    ratio        Decimal(18, 4)               COMMENT '解除限售比例',
    amount       Decimal(18, 2)               COMMENT '实际解禁金额',
    data_source  LowCardinality(String) DEFAULT 'akshare' COMMENT '数据来源',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol,'.')>0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(unlock_date)
ORDER BY (symbol, unlock_date)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "share_unlock"
DATABASE = "c3_fundamental"
CATEGORY_ID = "fundamental_share_unlock"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(unlock_date)"
ORDER_BY = "(symbol, unlock_date)"

INSERT_COLUMNS = "(symbol, unlock_date, shares, ratio, amount, data_source)"
