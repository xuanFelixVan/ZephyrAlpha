# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c3_fundamental_clickhouse.md
# [MODULE] schemas.categories.fundamental_analyst_forecast
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_fundamental_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] analyst_forecast 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->verify_schema_truth.py 报漂移+apply_fundamental_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/verify_schema_truth.py --table analyst_forecast
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""analyst_forecast（分析师预测）DDL-as-Code（category_id: fundamental_analyst_forecast, calc_mode: preload）。

本文件是 c3_fundamental.analyst_forecast 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

真源回写（#ARCH-CH-025 Schema 真源体系收口，Wave 1，2026-07-25）：
    audit_01 实测本表为 8 张裸 MergeTree 之一（违反 #ARCH-CH-002 全部 ReplacingMergeTree 裁定）。
    P0-8 已在 DB 层迁移至 ReplacingMergeTree（消除写前 DELETE mutations 累积反模式），
    但未回写 DDL-as-Code 真源——本文件补齐该真源断层，治本 100% AI 开发可维护性。

引擎选型：
    ReplacingMergeTree（无版本列）——同 (symbol, report_date) 重复行按插入顺序保留最后一条。
    PARTITION BY toYYYYMM(report_date)——按报告日期月分区。
    ORDER BY (symbol, report_date)——单标的多报告期点查友好。

审计列（audit 1.7 #ARCH-CH-022）：
    ingest_ts DateTime64(3,'UTC') DEFAULT now()（无 quality_flag，本表无质量门消费方）。
"""

from __future__ import annotations

# category_id: fundamental_analyst_forecast
# calc_mode: preload（回测时预加载到内存）

ANALYST_FORECAST_DDL = """
CREATE TABLE IF NOT EXISTS c3_fundamental.analyst_forecast
(
    report_date     Date                     COMMENT '报告日期',
    symbol          String                   COMMENT '证券代码',
    forecast_year   String                   COMMENT '预测年度',
    forecast_eps    Decimal(18, 4)           COMMENT '预测每股收益',
    forecast_pe     Decimal(18, 4)           COMMENT '预测市盈率',
    rating          String                   COMMENT '评级',
    analyst_count   UInt16                   COMMENT '分析师数量',
    data_source     LowCardinality(String) DEFAULT 'akshare' COMMENT '数据来源',
    ingest_ts       DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol,'.')>0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(report_date)
ORDER BY (symbol, report_date)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "analyst_forecast"
DATABASE = "c3_fundamental"
CATEGORY_ID = "fundamental_analyst_forecast"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(report_date)"
ORDER_BY = "(symbol, report_date)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
INSERT_COLUMNS = "(report_date, symbol, forecast_year, forecast_eps, forecast_pe, rating, analyst_count, data_source)"
