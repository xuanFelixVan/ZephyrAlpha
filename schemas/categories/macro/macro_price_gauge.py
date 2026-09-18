# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.macro.macro_price_gauge
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] macro_price_gauge 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""macro_price_gauge（价格总 gaug 表：CPI/PPI）DDL-as-Code（category_id: macro_price_gauge）.

D3 宏观高频第一梯队（altdata_line 09 清单 D3，2026-09-18 夜班施工）。
中国月度价格总指标宽表：CPI 当月指数/同比/环比/累计 + PPI 当月指数/同比/累计。

源（东方财富 datacenter，月度，fresh 实测 2026-08）：
    macro_china_cpi → cpi_index/cpi_yoy/cpi_mom/cpi_cum（2008- 起全国口径）
    macro_china_ppi → ppi_index/ppi_yoy/ppi_cum（2006- 起）

源选型说明：金十口径 macro_china_cpi_yearly/cpi_monthly/ppi_yearly 实测 2025-10 起
源端停更（尾部 nan 今值+预约行，2026-09-18 实查），故取东财口径为主源；
金十版退役前历史段如需预测值/前值（surprise 分析）另行评估。

与 c1_market.macro_data 的关系（查重声明）：
    macro_data=generic 长表（indicator_name 维度，既有 CPI 任务继续维护）；
    本表为宽表结构化数据集（固定数值列，回测口径不同），按
    骨架分类学判据 2（回测口径变了→拆）独立成表，不构成双真源。

PIT 双轴：report_date=事实时间锚（统计期月末）；ingest_ts=采集时间。
金十 publish_date 观察锚在本口径不可得（东财接口不含公布日），列不设。

引擎选型：
    ReplacingMergeTree（无版本列，重拉幂等去重）。
    PARTITION BY toYYYYMM(report_date)。
    ORDER BY (report_date)。
"""

from __future__ import annotations

# category_id: macro_price_gauge
# calc_mode: preload

MACRO_PRICE_GAUGE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.macro_price_gauge
(
    report_date   Date                        COMMENT '统计期月末(事实时间锚)',
    cpi_index     Nullable(Decimal(10, 4))    COMMENT 'CPI当月指数(上年同月=100)',
    cpi_yoy       Nullable(Decimal(10, 4))    COMMENT 'CPI当月同比(%)',
    cpi_mom       Nullable(Decimal(10, 4))    COMMENT 'CPI当月环比(%)',
    cpi_cum       Nullable(Decimal(10, 4))    COMMENT 'CPI累计指数(上年同期=100)',
    ppi_index     Nullable(Decimal(10, 4))    COMMENT 'PPI当月指数(上年同月=100)',
    ppi_yoy       Nullable(Decimal(10, 4))    COMMENT 'PPI当月同比(%)',
    ppi_cum       Nullable(Decimal(10, 4))    COMMENT 'PPI累计指数(上年同期=100)',
    data_source   LowCardinality(String)      DEFAULT 'akshare' COMMENT '数据来源',
    quality_flag  UInt8                       DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts     DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳(采集时间锚)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(report_date)
ORDER BY (report_date)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "macro_price_gauge"
DATABASE = "c1_market"
CATEGORY_ID = "macro_price_gauge"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(report_date)"
ORDER_BY = "(report_date)"

INSERT_COLUMNS = (
    "(report_date, cpi_index, cpi_yoy, cpi_mom, cpi_cum, ppi_index, ppi_yoy, ppi_cum, data_source, quality_flag)"
)
