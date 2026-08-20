# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_stock_list
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider; zephyr.data.implementations.miniqmt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] stock_list 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->apply_schema.py --verify退出码1
# [TESTS] tests/data/test_pit_query.py(survivorship_universe)
# [TTL] permanent
"""stock_list 表 DDL-as-Code（category_id: market_stock_list, calc_mode: preload）。

本文件是 c1_market.stock_list 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

SCD-2 时点版本化设计（#ARCH-CH-021 P0-1/P0-6，2026-07-23）：
    stock_list 采用 SCD-2（Slowly Changing Dimension Type 2）时点版本化，
    通过 valid_from/valid_to 列记录每只标的的生命周期，消除幸存者偏差：
    - valid_from DEFAULT toDate(list_date)：标的上市日（自动从 list_date 派生）
    - valid_to Nullable(Date)：标的退市日（NULL=当前有效，退市股=delist_date）
    - updated_at DEFAULT now()：记录更新时间

    回测时通过 pit_query.survivorship_universe(query_time) 过滤：
    valid_from <= query_time AND (valid_to IS NULL OR valid_to > query_time)
    确保回测 universe 仅含查询时点仍在市的标的（含未来退市但当时在市者）。

    退市股数据来源：akshare stock_info_sh_delist + stock_info_sz_delist
    （月度刷新任务 stock_list_delisted_refresh，capability=stock_list_delisted）

    引擎说明：ReplacingMergeTree（无版本列），ORDER BY (ts_code)
    同一 ts_code 的重复插入按插入顺序保留最后一条（覆盖式更新）。
    退市股 valid_to 在 akshare_provider._collect_delisted_rows 中显式写入（=delist_date），
    防月度刷新覆盖已回填的 SCD-2 数据。

    ingest_ts 审计列（2026-07-23 新增，audit 1.7 #ARCH-CH-025）：
    新行由 CH 自动填充入库时间；旧行按 DEFAULT 惰性求值（近似值）。
    不入 INSERT_COLUMNS（DEFAULT 自动填充）。
"""

from __future__ import annotations

# category_id: market_stock_list
# calc_mode: preload（回测时预加载到内存）

STOCK_LIST_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.stock_list
(
    ts_code              String                    COMMENT 'Tushare代码(000001.SZ)',
    symbol               String                    COMMENT '证券代码(000001)',
    name                 String                    COMMENT '证券简称',
    area                 String                    COMMENT '地域',
    industry             String                    COMMENT '所属行业',
    fullname             String                    COMMENT '全称',
    enname               String                    COMMENT '英文名',
    cn_spell             String                    COMMENT '拼音',
    market               String                    COMMENT '市场(A股/港股/美股)',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    currency             String                    COMMENT '币种',
    list_status          String                    COMMENT '上市状态(上市/退市/暂停)',
    list_date            Date                      COMMENT '上市日期',
    delist_date          Date                      COMMENT '退市日期(未退市=1970-01-01)',
    hs_hold              String                    COMMENT '同花顺概念',
    actual_controller    String                    COMMENT '实际控制人',
    controller_type      String                    COMMENT '控制人类型',
    valid_from           Date          DEFAULT toDate(list_date) COMMENT 'SCD-2生效起始日(#ARCH-CH-021 P0-1)',
    valid_to             Nullable(Date)             COMMENT 'SCD-2生效终止日(NULL=当前有效,退市股=delist_date)',
    updated_at           DateTime64(3, 'UTC')  DEFAULT now() COMMENT '记录更新时间',
    ingest_ts            DateTime64(3, 'UTC')  DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY (ts_code)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "stock_list"
DATABASE = "c1_market"
CATEGORY_ID = "market_stock_list"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "tuple()"
ORDER_BY = "(ts_code)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
# 注意：valid_to 需显式传入（退市股=delist_date，在市股=NULL/省略）
# valid_from/updated_at/ingest_ts 由 DEFAULT 自动填充
INSERT_COLUMNS = (
    "(ts_code, symbol, name, area, industry, fullname, enname, cn_spell, "
    "market, currency, list_status, list_date, delist_date, "
    "hs_hold, actual_controller, controller_type, valid_to)"
)
