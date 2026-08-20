# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_index_meta
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.c1_market_writer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] market_index_meta 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""market_index_meta 表 DDL-as-Code（category_id: market_index_meta, calc_mode: lazy）。

本文件是 c1_market.market_index_meta 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

来源：由 .runtime/_gen_truth_sources.py 从 ClickHouse system.tables/system.columns
反向生成（机构升级 DDL 真源回写，#ARCH-CH-025 Schema 真源体系收口）。

列清单：
#   sector_code: String
#   sector_name: String
#   valid_from: Date
#   valid_to: Nullable(Date)
#   updated_at: DateTime64(3, 'UTC')
#   ingest_ts: DateTime64(3, 'UTC')
"""

from __future__ import annotations

# category_id: market_index_meta
# calc_mode: lazy

MARKET_INDEX_META_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.market_index_meta
(
    sector_code              String,
    sector_name              String,
    valid_from               Date  DEFAULT today()  COMMENT 'SCD-2生效起始日',
    valid_to                 Nullable(Date)  COMMENT 'SCD-2生效终止日(NULL=当前有效)',
    updated_at               DateTime64(3, 'UTC')  DEFAULT now()  COMMENT '记录更新时间',
    ingest_ts                DateTime64(3, 'UTC')  DEFAULT now()
)
ENGINE = ReplacingMergeTree
ORDER BY (sector_code)
"""

# 表元数据
TABLE_NAME = "market_index_meta"
DATABASE = "c1_market"
CATEGORY_ID = "market_index_meta"
CALC_MODE = "lazy"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = ""
ORDER_BY = "(sector_code)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
INSERT_COLUMNS = "(sector_code, sector_name, valid_to)"
