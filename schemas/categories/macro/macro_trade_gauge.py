# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.macro.macro_trade_gauge
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] macro_trade_gauge 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""macro_trade_gauge（外需宽表：海关进出口当月/累计额+同比/环比）DDL-as-Code
（category_id: macro_trade_gauge）.

D3 宏观高频第一梯队（altdata_line 09 清单 D3，2026-09-18 夜班施工）。
中国月度海关进出口宽表：当月出口/进口额+同比+环比、年初累计出口/进口额+同比。

源：macro_china_hgjck（东财 datacenter RPT_ECONOMY_CUSTOMS，2008- 起，
fresh 实测 2026-08）。

单位核验（2026-09-18 双点交叉验证）：源字段 EXIT_BASE 原始值 401440956.924 对应
2026-08 当月出口，÷1e5=4014.41 亿美元（$401.4B），同比 25.0% 回代 2025-08 出口
3218 亿美元吻合、累计同比 19.3% 回代 Jan-Aug 2025 2.44 万亿美元吻合——判定源值
单位=千美元，本表统一换算为亿美元（源值/100000）落库，列名带 _usd100m 后缀
显式声明单位防误读。

PIT 双轴：report_date=事实时间锚（统计期月末）；ingest_ts=采集时间。

引擎选型：
    ReplacingMergeTree（无版本列，重拉幂等去重）。
    PARTITION BY toYYYYMM(report_date)。
    ORDER BY (report_date)。
"""

from __future__ import annotations

# category_id: macro_trade_gauge
# calc_mode: preload

MACRO_TRADE_GAUGE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.macro_trade_gauge
(
    report_date        Date                        COMMENT '统计期月末(事实时间锚)',
    export_usd100m     Nullable(Decimal(18, 4))    COMMENT '当月出口额(亿美元)',
    export_yoy         Nullable(Decimal(10, 4))    COMMENT '当月出口同比(%)',
    export_mom         Nullable(Decimal(10, 4))    COMMENT '当月出口环比(%)',
    import_usd100m     Nullable(Decimal(18, 4))    COMMENT '当月进口额(亿美元)',
    import_yoy         Nullable(Decimal(10, 4))    COMMENT '当月进口同比(%)',
    import_mom         Nullable(Decimal(10, 4))    COMMENT '当月进口环比(%)',
    export_cum_usd100m Nullable(Decimal(18, 4))    COMMENT '年初累计出口额(亿美元)',
    export_cum_yoy     Nullable(Decimal(10, 4))    COMMENT '累计出口同比(%)',
    import_cum_usd100m Nullable(Decimal(18, 4))    COMMENT '年初累计进口额(亿美元)',
    import_cum_yoy     Nullable(Decimal(10, 4))    COMMENT '累计进口同比(%)',
    data_source        LowCardinality(String)      DEFAULT 'akshare' COMMENT '数据来源',
    quality_flag       UInt8                       DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts          DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳(采集时间锚)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(report_date)
ORDER BY (report_date)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "macro_trade_gauge"
DATABASE = "c1_market"
CATEGORY_ID = "macro_trade_gauge"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(report_date)"
ORDER_BY = "(report_date)"

INSERT_COLUMNS = (
    "(report_date, export_usd100m, export_yoy, export_mom, import_usd100m, import_yoy, import_mom, "
    "export_cum_usd100m, export_cum_yoy, import_cum_usd100m, import_cum_yoy, data_source, quality_flag)"
)
