# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_index_list
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] index_list 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""index_list 表 DDL-as-Code（category_id: market_index_list, calc_mode: preload）.

P0-6 SCD-2 真源回写（#ARCH-CH-021/#ARCH-CH-025, 2026-07-25）：
    本文件从 ClickHouse 实际表结构转录为 DDL-as-Code 真源，消除"DB 有表无真源"漂移债务。
    index_list 采用 SCD-2 时点版本化（valid_from/valid_to），消除幸存者偏差。

    SCD-2 字段：
    - valid_from DEFAULT today()/toDate(xxx)：记录生效起始日
    - valid_to Nullable(Date)：记录生效终止日（NULL=当前有效）
    - updated_at DEFAULT now()：记录更新时间
    - ingest_ts DEFAULT now()：入库时间戳（audit 1.7 #ARCH-CH-025）
"""

from __future__ import annotations

# category_id: market_index_list
# calc_mode: preload（SCD 维度表，回测时预加载到内存）

INDEX_LIST_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.index_list
(
    ts_code     String               COMMENT 'ts_code',
    name        String               COMMENT 'name',
    market      String               COMMENT 'market',
    publisher   String               COMMENT 'publisher',
    category    String               COMMENT 'category',
    base_date   Date                 COMMENT 'base_date',
    base_point  Float64              COMMENT 'base_point',
    list_date   Date                 COMMENT 'list_date',
    symbol_num  String               COMMENT 'symbol_num',
    market_id   Float64              COMMENT 'market_id',
    valid_from  Date                 DEFAULT toDate(list_date) COMMENT 'SCD-2生效起始日',
    valid_to    Nullable(Date)       COMMENT 'SCD-2生效终止日(NULL=当前有效)',
    updated_at  DateTime64(3, 'UTC') DEFAULT now() COMMENT '记录更新时间',
    ingest_ts   DateTime64(3, 'UTC') DEFAULT now() COMMENT 'ingest_ts'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY (ts_code)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "index_list"
DATABASE = "c1_market"
CATEGORY_ID = "market_index_list"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "tuple()"
ORDER_BY = "(ts_code)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
# valid_to 需显式传入（退市/失效=终止日，有效=NULL/省略）
INSERT_COLUMNS = (
    "(ts_code, name, market, publisher, category, base_date, base_point, , list_date, symbol_num, market_id, valid_to)"
)
