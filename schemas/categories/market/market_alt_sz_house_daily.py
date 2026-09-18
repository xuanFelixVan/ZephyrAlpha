# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market.market_alt_sz_house_daily
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] alt_sz_house_daily 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""深圳楼市日度成交（2 系列并表：一手商品房/二手房，深圳市住房和建设局，
深圳开放数据平台 appKey 通道）。按区×日度成交套数/面积，地产链高频因子原料。
"""

from __future__ import annotations

# category_id: market_alt_sz_house_daily
# calc_mode: preload

MARKET_ALT_SZ_HOUSE_DAILY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_sz_house_daily
(
    series_code    LowCardinality(String) COMMENT '系列: house_new/house_second',
    src_id         String                 COMMENT '源表ID(幂等键)',
    tj_date        Date                   COMMENT '统计日期',
    zone           String                 COMMENT '区域',
    report_catalog String                 COMMENT '报告目录(一手)',
    house_usage    String                 COMMENT '房屋用途(二手)',
    ks_num         Nullable(Int64)        COMMENT '可售套数(一手)',
    ks_area        Nullable(Float64)      COMMENT '可售面积(一手)',
    cj_num         Float64                COMMENT '成交套数',
    cj_area        Float64                COMMENT '成交面积',
    ingest_ts      DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(tj_date)
ORDER BY (series_code, src_id)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_sz_house_daily"
DATABASE = "c1_market"
CATEGORY_ID = "market_alt_sz_house_daily"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(tj_date)"
ORDER_BY = "(series_code, src_id)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(series_code, src_id, tj_date, zone, report_catalog, house_usage, ks_num, ks_area, cj_num, cj_area)"
