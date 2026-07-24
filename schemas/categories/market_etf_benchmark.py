# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_etf_benchmark
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] etf_benchmark 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [TTL] permanent
"""etf_benchmark 表 DDL-as-Code（category_id: market_etf_benchmark, calc_mode: preload）.

P0-6 SCD-2 真源回写（#ARCH-CH-021/#ARCH-CH-025, 2026-07-25）：
    本文件从 ClickHouse 实际表结构转录为 DDL-as-Code 真源，消除"DB 有表无真源"漂移债务。
    etf_benchmark 采用 SCD-2 时点版本化（valid_from/valid_to），消除幸存者偏差。

    SCD-2 字段：
    - valid_from DEFAULT today()/toDate(xxx)：记录生效起始日
    - valid_to Nullable(Date)：记录生效终止日（NULL=当前有效）
    - updated_at DEFAULT now()：记录更新时间
    - ingest_ts DEFAULT now()：入库时间戳（audit 1.7 #ARCH-CH-025）
"""

from __future__ import annotations

# category_id: market_etf_benchmark
# calc_mode: preload（SCD 维度表，回测时预加载到内存）

ETF_BENCHMARK_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.etf_benchmark
(
    index_code        String               COMMENT 'index_code',
    index_full_name   String               COMMENT 'index_full_name',
    index_short_name  String               COMMENT 'index_short_name',
    publisher         String               COMMENT 'publisher',
    publish_date      Date                 COMMENT 'publish_date',
    base_date         Date                 COMMENT 'base_date',
    base_point        Float64              COMMENT 'base_point',
    adjust_cycle      String               COMMENT 'adjust_cycle',
    valid_from        Date                 DEFAULT today() COMMENT 'SCD-2生效起始日',
    valid_to          Nullable(Date)       COMMENT 'SCD-2生效终止日(NULL=当前有效)',
    updated_at        DateTime64(3, 'UTC') DEFAULT now() COMMENT '记录更新时间',
    ingest_ts         DateTime64(3, 'UTC') DEFAULT now() COMMENT 'ingest_ts'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY (index_code)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "etf_benchmark"
DATABASE = "c1_market"
CATEGORY_ID = "market_etf_benchmark"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "tuple()"
ORDER_BY = "(index_code)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
# valid_to 需显式传入（退市/失效=终止日，有效=NULL/省略）
INSERT_COLUMNS = (
    "(index_code, index_full_name, index_short_name, publisher, publish_date, "
    ", base_date, base_point, adjust_cycle, valid_to)"
)
