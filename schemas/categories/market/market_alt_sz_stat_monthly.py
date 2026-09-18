# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market.market_alt_sz_stat_monthly
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] alt_sz_stat_monthly 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""深圳统计月报长表（深圳市统计局统计月报族 7 系列并表：国民经济核算/物价/
财政金融/运输/对外贸易/统计快报/固定资产投资，深圳开放数据平台 appKey 通道）。

长表 (series_code, report_ym, zbmc) 粒度：指标名作行键、通用数值列 + 原始行 JSON
无损留存（各系列列名不一：BENYUE/BY=本月，BYZLJ/BNBJD=累计，LJTB=累计同比）。
指标口径以 ZBMC+raw 为准，消费端按 series_code+zbmc 取数。
"""

from __future__ import annotations

# category_id: market_alt_sz_stat_monthly
# calc_mode: preload

MARKET_ALT_SZ_STAT_MONTHLY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_sz_stat_monthly
(
    series_code  LowCardinality(String) COMMENT '系列: stat_gdp/stat_price/stat_fiscal/stat_transport/stat_trade/stat_quick/stat_fixinv',
    report_ym    String                 COMMENT '报告期 YYYYMM',
    report_date  Date                   COMMENT '报告期首日(派生,分区锚)',
    zbmc         String                 COMMENT '指标名称(源 ZBMC)',
    dw           String                 COMMENT '单位(源 DW)',
    xh           UInt16                 COMMENT '源表序号',
    val_month    Nullable(Float64)      COMMENT '本月值(BENYUE/BY)',
    val_cum      Nullable(Float64)      COMMENT '累计值(BYZLJ/BNBJD等)',
    yoy_cum      Nullable(Float64)      COMMENT '累计同比(LJTB等)',
    raw          String                 COMMENT '原始行JSON(无损)',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(report_date)
ORDER BY (series_code, report_ym, zbmc)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_sz_stat_monthly"
DATABASE = "c1_market"
CATEGORY_ID = "market_alt_sz_stat_monthly"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(report_date)"
ORDER_BY = "(series_code, report_ym, zbmc)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(series_code, report_ym, report_date, zbmc, dw, xh, val_month, val_cum, yoy_cum, raw)"
