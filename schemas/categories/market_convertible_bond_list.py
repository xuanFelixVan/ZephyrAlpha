# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_convertible_bond_list
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] convertible_bond_list 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""convertible_bond_list 表 DDL-as-Code（category_id: market_convertible_bond_list, calc_mode: preload）.

P0-6 SCD-2 真源回写（#ARCH-CH-021/#ARCH-CH-025, 2026-07-25）：
    本文件从 ClickHouse 实际表结构转录为 DDL-as-Code 真源，消除"DB 有表无真源"漂移债务。
    convertible_bond_list 采用 SCD-2 时点版本化（valid_from/valid_to），消除幸存者偏差。

    SCD-2 字段：
    - valid_from DEFAULT today()/toDate(xxx)：记录生效起始日
    - valid_to Nullable(Date)：记录生效终止日（NULL=当前有效）
    - updated_at DEFAULT now()：记录更新时间
    - ingest_ts DEFAULT now()：入库时间戳（audit 1.7 #ARCH-CH-025）
"""

from __future__ import annotations

# category_id: market_convertible_bond_list
# calc_mode: preload（SCD 维度表，回测时预加载到内存）

CONVERTIBLE_BOND_LIST_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.convertible_bond_list
(
    bond_code              String               COMMENT 'bond_code',
    bond_name              String               COMMENT 'bond_name',
    bond_short_name        String               COMMENT 'bond_short_name',
    convert_code           String               COMMENT 'convert_code',
    stock_code             String               COMMENT 'stock_code',
    stock_name             String               COMMENT 'stock_name',
    issue_term             Float64              COMMENT 'issue_term',
    par_value              Float64              COMMENT 'par_value',
    issue_price            Float64              COMMENT 'issue_price',
    issue_amount           Float64              COMMENT 'issue_amount',
    bond_balance           Float64              COMMENT 'bond_balance',
    start_date             Date                 COMMENT 'start_date',
    end_date               Date                 COMMENT 'end_date',
    rate_type              String               COMMENT 'rate_type',
    coupon_rate            Float64              COMMENT 'coupon_rate',
    comp_rate              Float64              COMMENT 'comp_rate',
    pay_count              UInt16               COMMENT 'pay_count',
    list_date              Date                 COMMENT 'list_date',
    delist_date            Date                 COMMENT 'delist_date',
    list_place             String               COMMENT 'list_place',
    convert_start          Date                 COMMENT 'convert_start',
    convert_end            Date                 COMMENT 'convert_end',
    stop_convert           Date                 COMMENT 'stop_convert',
    initial_convert_price  Float64              COMMENT 'initial_convert_price',
    latest_convert_price   Float64              COMMENT 'latest_convert_price',
    rate_desc              String               COMMENT 'rate_desc',
    redeem_price           Float64              COMMENT 'redeem_price',
    issue_credit           String               COMMENT 'issue_credit',
    latest_credit          String               COMMENT 'latest_credit',
    latest_agency          String               COMMENT 'latest_agency',
    valid_from             Date                 DEFAULT toDate(list_date) COMMENT 'SCD-2生效起始日',
    valid_to               Nullable(Date)       COMMENT 'SCD-2生效终止日(NULL=当前有效)',
    updated_at             DateTime64(3, 'UTC') DEFAULT now() COMMENT '记录更新时间',
    ingest_ts              DateTime64(3, 'UTC') DEFAULT now() COMMENT 'ingest_ts'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY (bond_code)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "convertible_bond_list"
DATABASE = "c1_market"
CATEGORY_ID = "market_convertible_bond_list"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "tuple()"
ORDER_BY = "(bond_code)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
# valid_to 需显式传入（退市/失效=终止日，有效=NULL/省略）
INSERT_COLUMNS = (
    "(bond_code, bond_name, bond_short_name, convert_code, stock_code, "
    ", stock_name, issue_term, par_value, issue_price, issue_amount, "
    ", bond_balance, start_date, end_date, rate_type, coupon_rate, comp_rate, "
    ", pay_count, list_date, delist_date, list_place, convert_start, "
    ", convert_end, stop_convert, initial_convert_price, latest_convert_price, "
    ", rate_desc, redeem_price, issue_credit, latest_credit, latest_agency, "
    ", valid_to)"
)
