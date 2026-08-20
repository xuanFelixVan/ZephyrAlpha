# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.fundamental_industry_class
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.c1_market_writer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] industry_class 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""industry_class 表 DDL-as-Code（category_id: fundamental_industry_class, calc_mode: lazy）。

本文件是 c1_market.industry_class 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

来源：由 .runtime/_gen_truth_sources.py 从 ClickHouse system.tables/system.columns
反向生成（机构升级 DDL 真源回写，#ARCH-CH-025 Schema 真源体系收口）。

列清单：
#   symbol: String
#   industry_sw: String
#   industry_zsi: String
#   industry_level: UInt8
#   data_source: LowCardinality(String)
#   valid_from: Date
#   valid_to: Nullable(Date)
#   updated_at: DateTime64(3, 'UTC')
#   ingest_ts: DateTime64(3, 'UTC')
"""

from __future__ import annotations

# category_id: fundamental_industry_class
# calc_mode: lazy

FUNDAMENTAL_INDUSTRY_CLASS_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.industry_class
(
    symbol                   String,
    industry_sw              String,
    industry_zsi             String,
    industry_level           UInt8,
    data_source              LowCardinality(String)  DEFAULT 'tushare',
    valid_from               Date  DEFAULT today()  COMMENT 'SCD-2生效起始日',
    valid_to                 Nullable(Date)  COMMENT 'SCD-2生效终止日(NULL=当前有效)',
    updated_at               DateTime64(3, 'UTC')  DEFAULT now()  COMMENT '记录更新时间',
    ingest_ts                DateTime64(3, 'UTC')  DEFAULT now(),
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
-- 排序键含 industry_level：一只股票有多级行业分类（level 1/2/3），
-- 单独以 symbol 为排序键会导致 ReplacingMergeTree merge 时同 symbol 多行塌缩丢数据
-- （#ARCH-CH-INDUSTRY-CLASS-MIGRATE 治本，2026-08-03，FINAL 实证 000001 丢 level=3）
ORDER BY (symbol, industry_level)
"""

# 表元数据
TABLE_NAME = "industry_class"
DATABASE = "c1_market"
CATEGORY_ID = "fundamental_industry_class"
CALC_MODE = "lazy"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = ""
ORDER_BY = "(symbol, industry_level)"  # 含 industry_level 防止 merge 塌缩多级分类行

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
INSERT_COLUMNS = "(symbol, industry_sw, industry_zsi, industry_level, valid_to)"
