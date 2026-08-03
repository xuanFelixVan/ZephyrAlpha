# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_concept_board_constituent
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] concept_board_constituent 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""concept_board_constituent 表 DDL-as-Code（category_id: market_concept_board_constituent, calc_mode: preload）.

P0-6 SCD-2 真源回写（#ARCH-CH-021/#ARCH-CH-025, 2026-07-25）：
    本文件从 ClickHouse 实际表结构转录为 DDL-as-Code 真源，消除"DB 有表无真源"漂移债务。
    concept_board_constituent 采用 SCD-2 时点版本化（valid_from/valid_to），消除幸存者偏差。

    SCD-2 字段：
    - valid_from DEFAULT today()/toDate(xxx)：记录生效起始日
    - valid_to Nullable(Date)：记录生效终止日（NULL=当前有效）
    - updated_at DEFAULT now()：记录更新时间
    - ingest_ts DEFAULT now()：入库时间戳（audit 1.7 #ARCH-CH-025）
"""

from __future__ import annotations

# category_id: market_concept_board_constituent
# calc_mode: preload（SCD 维度表，回测时预加载到内存）

CONCEPT_BOARD_CONSTITUENT_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.concept_board_constituent
(
    board_code   String                 COMMENT 'board_code',
    symbol       String                 COMMENT 'symbol',
    data_source  LowCardinality(String) DEFAULT 'akshare' COMMENT 'data_source',
    valid_from   Date                   DEFAULT today() COMMENT 'SCD-2生效起始日',
    valid_to     Nullable(Date)         COMMENT 'SCD-2生效终止日(NULL=当前有效)',
    updated_at   DateTime64(3, 'UTC')   DEFAULT now() COMMENT '记录更新时间',
    ingest_ts    DateTime64(3, 'UTC')   DEFAULT now() COMMENT 'ingest_ts',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY board_code, symbol
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "concept_board_constituent"
DATABASE = "c1_market"
CATEGORY_ID = "market_concept_board_constituent"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "tuple()"
ORDER_BY = "board_code, symbol"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
# valid_to 需显式传入（退市/失效=终止日，有效=NULL/省略）
INSERT_COLUMNS = "(board_code, symbol, valid_to)"
