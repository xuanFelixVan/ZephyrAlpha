# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_index_weight
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.c1_market_writer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] index_weight 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->apply_schema.py --verify退出码1
# [TESTS] tests/data/test_schema_alignment.py
# [TTL] permanent
"""index_weight 表 DDL-as-Code（category_id: market_index_weight, calc_mode: none）。

本文件是 c1_market.index_weight 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

SCD-2 时点版本（#ARCH-CH-021 P0-6, 2026-07-23）：
    新增 valid_from/valid_to/updated_at 三列支持时点查询。
    指数成分股权重随指数调整而变化，SCD-2 保留历史版本。
    valid_from=trade_date（数据生效日），valid_to=NULL（当前有效）。
"""

from __future__ import annotations

# category_id: market_index_weight
# calc_mode: none（元数据表，月初刷新，不预加载）

INDEX_WEIGHT_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.index_weight
(
    trade_date   Date                    COMMENT '交易日期',
    index_code   String                  COMMENT '指数代码(如000300.SH)',
    symbol       String                  COMMENT '成分股代码',
    weight       Decimal(10,6)           COMMENT '权重(%)',
    data_source  LowCardinality(String)  COMMENT '数据来源',
    ingest_ts    DateTime64(3, 'UTC')  DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)',
    valid_from   Date          DEFAULT toDate(trade_date) COMMENT 'SCD-2生效起始日(#ARCH-CH-021 P0-6)',
    valid_to     Nullable(Date)          COMMENT 'SCD-2生效终止日(NULL=当前有效)',
    updated_at   DateTime64(3, 'UTC')  DEFAULT now() COMMENT '记录更新时间(#ARCH-CH-021 P0-6)',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, index_code, symbol)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "index_weight"
DATABASE = "c1_market"
CATEGORY_ID = "market_index_weight"
CALC_MODE = "none"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(trade_date, index_code, symbol)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
INSERT_COLUMNS = "(trade_date, index_code, symbol, weight, data_source)"
