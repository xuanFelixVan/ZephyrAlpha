# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.macro_edb_data
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.c1_market_writer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] edb_data 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""edb_data 表 DDL-as-Code（category_id: macro_edb_data, calc_mode: lazy）。

本文件是 c1_market.edb_data 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

来源：由 .runtime/_gen_truth_sources.py 从 ClickHouse system.tables/system.columns
反向生成（机构升级 DDL 真源回写，#ARCH-CH-025 Schema 真源体系收口）。

列清单：
#   report_date: Date
#   indicator_code: String
#   indicator_name: String
#   indicator_value: Float64
#   data_source: LowCardinality(String)
#   ingest_ts: DateTime64(3, 'UTC')
"""

from __future__ import annotations

# category_id: macro_edb_data
# calc_mode: lazy

MACRO_EDB_DATA_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.edb_data
(
    report_date              Date  COMMENT '报告日期',
    indicator_code           String  COMMENT '指标代码',
    indicator_name           String  COMMENT '指标名称',
    indicator_value          Float64  COMMENT '指标值',
    data_source              LowCardinality(String)  COMMENT '数据来源(原ifind EDB已退役2026-08-14,表0行停更)',
    ingest_ts                DateTime64(3, 'UTC')  DEFAULT now()
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(report_date)
ORDER BY indicator_code, report_date
"""

# 表元数据
TABLE_NAME = "edb_data"
DATABASE = "c1_market"
CATEGORY_ID = "macro_edb_data"
CALC_MODE = "lazy"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(report_date)"
ORDER_BY = "indicator_code, report_date"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
INSERT_COLUMNS = "(report_date, indicator_code, indicator_name, indicator_value)"
