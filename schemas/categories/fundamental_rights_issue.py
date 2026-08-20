# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c3_fundamental_clickhouse.md
# [MODULE] schemas.categories.fundamental_rights_issue
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_fundamental_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] rights_issue 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->verify_schema_truth.py 报漂移+apply_fundamental_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/verify_schema_truth.py --table rights_issue
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""rights_issue（分红配股）DDL-as-Code（category_id: fundamental_rights_issue）。

本文件是 c3_fundamental.rights_issue 表结构的唯一真源。

真源回写（#ARCH-CH-025，Wave 1，2026-07-25）：P0-8 DB 层已迁移 ReplacingMergeTree，本文件补齐真源。

引擎选型：
    ReplacingMergeTree（无版本列）。
    PARTITION BY toYYYYMM(announce_date)——按公告日期月分区。
    ORDER BY (symbol, announce_date, type)——单标的多类型方案点查友好。
"""

from __future__ import annotations

# category_id: fundamental_rights_issue
# calc_mode: preload

RIGHTS_ISSUE_DDL = """
CREATE TABLE IF NOT EXISTS c3_fundamental.rights_issue
(
    symbol              String              COMMENT '证券代码',
    stock_name          String              COMMENT '证券名称',
    announce_date       Date                COMMENT '公告日期',
    bonus_shares        Nullable(Float64)   COMMENT '送股(股)',
    capitalized_shares  Nullable(Float64)   COMMENT '转增(股)',
    dividend_pre_tax    Nullable(Float64)   COMMENT '派息(税前)(元)',
    status              String              COMMENT '进度',
    ex_date             Nullable(Date)      COMMENT '除权除息日',
    record_date         Nullable(Date)      COMMENT '股权登记日',
    listing_date        Nullable(Date)      COMMENT '红股上市日',
    type                String              COMMENT '类型(分红/配股)',
    rights_ratio        Nullable(Float64)   COMMENT '配股方案(每10股配股股数)',
    rights_price        Nullable(Float64)   COMMENT '配股价格(元)',
    base_capital        Nullable(Float64)   COMMENT '基准股本(股)',
    ex_rights_date      Nullable(Date)      COMMENT '除权日',
    payment_start       Nullable(Date)      COMMENT '缴款起始日',
    payment_end         Nullable(Date)      COMMENT '缴款终止日',
    rights_listing_date Nullable(Date)      COMMENT '配股上市日',
    total_funds_raised  Nullable(Float64)   COMMENT '募集资金合计(元)',
    data_source         String              COMMENT '数据来源',
    quality_flag        UInt8 DEFAULT 1     COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts           DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol,'.')>0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(announce_date)
ORDER BY (symbol, announce_date, type)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "rights_issue"
DATABASE = "c3_fundamental"
CATEGORY_ID = "fundamental_rights_issue"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(announce_date)"
ORDER_BY = "(symbol, announce_date, type)"

INSERT_COLUMNS = (
    "(symbol, stock_name, announce_date, bonus_shares, capitalized_shares, "
    "dividend_pre_tax, status, ex_date, record_date, listing_date, type, "
    "rights_ratio, rights_price, base_capital, ex_rights_date, payment_start, "
    "payment_end, rights_listing_date, total_funds_raised, data_source, quality_flag)"
)
