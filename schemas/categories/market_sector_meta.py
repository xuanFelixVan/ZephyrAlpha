# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_sector_meta
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.c1_market_writer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] sector_meta 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->apply_schema.py --verify退出码1
# [TESTS] tests/data/test_schema_alignment.py
# [TTL] permanent
"""sector_meta 表 DDL-as-Code（category_id: market_sector_meta, calc_mode: none）。

本文件是 c1_market.sector_meta 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

SCD-2 时点版本（#ARCH-CH-021 P0-6, 2026-07-23）：
    新增 valid_from/valid_to/updated_at 三列支持时点查询。
    板块元数据随成分股调整而变化，SCD-2 保留历史版本。
    valid_from=trade_date，valid_to=NULL（当前有效）。

Float64→Decimal 治本修复（Phase 3-A, 2026-07-23）：
    total_mv/float_mv: Float64→Decimal(18,2)（市值精度治本）
    float_share: Float64→Decimal(18,4)（股本精度治本）
"""

from __future__ import annotations

# category_id: market_sector_meta
# calc_mode: none（元数据表，日频更新）

SECTOR_META_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.sector_meta
(
    sector_code      String           COMMENT '板块代码',
    trade_date       Date             COMMENT '交易日期',
    sector_name      String           COMMENT '板块名称',
    sector_type      String           COMMENT '板块类型',
    constituent_num  UInt16           COMMENT '成分股数量',
    float_share      Decimal(18,4)    COMMENT '流通股本',
    total_mv         Decimal(18,2)    COMMENT '总市值(元)',
    float_mv         Decimal(18,2)    COMMENT '流通市值(元)',
    ingest_ts        DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)',
    valid_from       Date      DEFAULT toDate(trade_date) COMMENT 'SCD-2生效起始日(#ARCH-CH-021 P0-6)',
    valid_to         Nullable(Date)   COMMENT 'SCD-2生效终止日(NULL=当前有效)',
    updated_at       DateTime64(3, 'UTC') DEFAULT now() COMMENT '记录更新时间(#ARCH-CH-021 P0-6)'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY (sector_code, trade_date)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "sector_meta"
DATABASE = "c1_market"
CATEGORY_ID = "market_sector_meta"
CALC_MODE = "none"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "tuple()"
ORDER_BY = "(sector_code, trade_date)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
INSERT_COLUMNS = "(sector_code, trade_date, sector_name, sector_type, constituent_num, float_share, total_mv, float_mv)"
