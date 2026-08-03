# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_sector_constituent
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] sector_constituent 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""sector_constituent 表 DDL-as-Code（category_id: market_sector_constituent, calc_mode: preload）.

P0-6 SCD-2 真源回写（#ARCH-CH-021/#ARCH-CH-025, 2026-07-25）：
    本文件从 ClickHouse 实际表结构转录为 DDL-as-Code 真源，消除"DB 有表无真源"漂移债务。
    sector_constituent 采用 SCD-2 时点版本化（valid_from/valid_to），消除幸存者偏差。

    SCD-2 字段：
    - valid_from DEFAULT today()/toDate(xxx)：记录生效起始日
    - valid_to Nullable(Date)：记录生效终止日（NULL=当前有效）
    - updated_at DEFAULT now()：记录更新时间
    - ingest_ts DEFAULT now()：入库时间戳（audit 1.7 #ARCH-CH-025）
"""

from __future__ import annotations

# category_id: market_sector_constituent
# calc_mode: preload（SCD 维度表，回测时预加载到内存）

SECTOR_CONSTITUENT_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.sector_constituent
(
    sector_code  String               COMMENT '板块代码 880201.SH',
    sector_name  String               COMMENT '板块名称 种植业',
    stock_code   String               COMMENT '成分股代码 000711.SZ',
    update_date  Date                 COMMENT '更新日期',
    data_source  String               COMMENT '数据源 tqcenter',
    fetched_at   DateTime64(3, 'UTC') COMMENT '获取时间',
    valid_from   Date                 DEFAULT today() COMMENT 'SCD-2生效起始日',
    valid_to     Nullable(Date)       COMMENT 'SCD-2生效终止日(NULL=当前有效)',
    updated_at   DateTime64(3, 'UTC') DEFAULT now() COMMENT '记录更新时间',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now() COMMENT 'ingest_ts'
)
ENGINE = ReplacingMergeTree(fetched_at)
PARTITION BY toYYYYMM(update_date)
ORDER BY sector_code, stock_code
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "sector_constituent"
DATABASE = "c1_market"
CATEGORY_ID = "market_sector_constituent"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree(fetched_at)"
PARTITION_KEY = "toYYYYMM(update_date)"
ORDER_BY = "sector_code, stock_code"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
# valid_to 需显式传入（退市/失效=终止日，有效=NULL/省略）
INSERT_COLUMNS = "(sector_code, sector_name, stock_code, update_date, data_source, , fetched_at, valid_to)"
