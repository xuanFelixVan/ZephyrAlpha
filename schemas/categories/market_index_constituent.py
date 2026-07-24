# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_index_constituent
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] index_constituent 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [TTL] permanent
"""index_constituent 表 DDL-as-Code（category_id: market_index_constituent, calc_mode: preload）.

P0-6 SCD-2 真源回写（#ARCH-CH-021/#ARCH-CH-025, 2026-07-25）：
    本文件从 ClickHouse 实际表结构转录为 DDL-as-Code 真源，消除"DB 有表无真源"漂移债务。
    index_constituent 采用 SCD-2 时点版本化（valid_from/valid_to），消除幸存者偏差。

    SCD-2 字段：
    - valid_from DEFAULT today()/toDate(xxx)：记录生效起始日
    - valid_to Nullable(Date)：记录生效终止日（NULL=当前有效）
    - updated_at DEFAULT now()：记录更新时间
    - ingest_ts DEFAULT now()：入库时间戳（audit 1.7 #ARCH-CH-025）
"""

from __future__ import annotations

# category_id: market_index_constituent
# calc_mode: preload（SCD 维度表，回测时预加载到内存）

INDEX_CONSTITUENT_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.index_constituent
(
    trade_date   Date                   COMMENT 'trade_date',
    index_code   String                 COMMENT 'index_code',
    symbol       String                 COMMENT 'symbol',
    weight       Decimal(8, 4)          COMMENT 'weight',
    action       String                 COMMENT 'action',
    data_source  LowCardinality(String) DEFAULT 'ifind' COMMENT 'data_source',
    valid_from   Date                   DEFAULT toDate(trade_date) COMMENT 'SCD-2生效起始日',
    valid_to     Nullable(Date)         COMMENT 'SCD-2生效终止日(NULL=当前有效)',
    updated_at   DateTime64(3, 'UTC')   DEFAULT now() COMMENT '记录更新时间',
    ingest_ts    DateTime64(3, 'UTC')   DEFAULT now() COMMENT 'ingest_ts'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY index_code, trade_date
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "index_constituent"
DATABASE = "c1_market"
CATEGORY_ID = "market_index_constituent"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "index_code, trade_date"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
# valid_to 需显式传入（退市/失效=终止日，有效=NULL/省略）
INSERT_COLUMNS = "(trade_date, index_code, symbol, weight, action, valid_to)"
