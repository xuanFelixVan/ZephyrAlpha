# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c3_fundamental_clickhouse.md
# [MODULE] schemas.categories.fundamental_equity_pledge_detail
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_fundamental_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] equity_pledge_detail 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->verify_schema_truth.py 报漂移+apply_fundamental_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/verify_schema_truth.py --table equity_pledge_detail
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""equity_pledge_detail（股权质押明细）DDL-as-Code（category_id: fundamental_equity_pledge_detail）。

本文件是 c3_fundamental.equity_pledge_detail 表结构的唯一真源。

真源回写（#ARCH-CH-025，Wave 1，2026-07-25）：P0-8 DB 层已迁移 ReplacingMergeTree，本文件补齐真源。

引擎选型：
    ReplacingMergeTree（无版本列）。
    PARTITION BY toYYYYMM(announce_date)——按公告日期月分区。
    ORDER BY (symbol, announce_date, shareholder_name)——单标的多股东点查友好。

注：pledge_shares/total_holdings 等 Float64 字段为上游口径（万股），
    非 #ARCH-CH-026 Decimal 迁移范围（该裁定仅覆盖财务三表金额字段）。
"""

from __future__ import annotations

# category_id: fundamental_equity_pledge_detail
# calc_mode: preload

EQUITY_PLEDGE_DETAIL_DDL = """
CREATE TABLE IF NOT EXISTS c3_fundamental.equity_pledge_detail
(
    symbol             String              COMMENT '证券代码',
    announce_date      Date                COMMENT '公告日期',
    shareholder_name   String              COMMENT '股东名称',
    shareholder_type   String              COMMENT '股东类型',
    pledge_shares      Nullable(Float64)   COMMENT '质押数量(万股)',
    pledge_start_date  Nullable(Date)      COMMENT '质押开始日期',
    pledge_end_date    Nullable(Date)      COMMENT '质押结束日期',
    is_released        Nullable(Int32)     COMMENT '是否已解押',
    release_date       Nullable(Date)      COMMENT '解押日期',
    pledgee            String              COMMENT '质押方',
    total_holdings     Nullable(Float64)   COMMENT '持股总数(万股)',
    total_pledged      Nullable(Float64)   COMMENT '质押总数(万股)',
    pledge_ratio       Nullable(Float64)   COMMENT '本次质押占总股本比例(%)',
    holding_ratio      Nullable(Float64)   COMMENT '持股总数占总股本比例(%)',
    is_buyback         Nullable(Int32)     COMMENT '是否涉及回购',
    remark             String              COMMENT '备注',
    data_source        String              COMMENT '数据来源',
    quality_flag       UInt8 DEFAULT 1     COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts          DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol,'.')>0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(announce_date)
ORDER BY (symbol, announce_date, shareholder_name)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "equity_pledge_detail"
DATABASE = "c3_fundamental"
CATEGORY_ID = "fundamental_equity_pledge_detail"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(announce_date)"
ORDER_BY = "(symbol, announce_date, shareholder_name)"

INSERT_COLUMNS = (
    "(symbol, announce_date, shareholder_name, shareholder_type, pledge_shares, "
    "pledge_start_date, pledge_end_date, is_released, release_date, pledgee, "
    "total_holdings, total_pledged, pledge_ratio, holding_ratio, is_buyback, "
    "remark, data_source, quality_flag)"
)
