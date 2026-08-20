# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.fundamental_cashflow_statement
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_fundamental_tables_ddl; zephyr.data.implementations.miniqmt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] cashflow_statement 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->apply_fundamental_tables_ddl.py --verify退出码1
# [TESTS] scripts/ch/apply_fundamental_tables_ddl.py --verify (smoke test)
# [TTL] permanent
"""cashflow_statement（现金流量表）DDL-as-Code（category_id: fundamental_cashflow_statement, calc_mode: preload）。

本文件是 c3_fundamental.cashflow_statement 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

精度裁定（audit 1.2 #ARCH-CH-026，2026-07-23 治本）：
    金额字段由 Float64 迁移至 Nullable(Decimal(18,2))——消除二进制浮点精度隐患。
    max 现金流 1.95T < Decimal(18,2) 上限 10^16 安全。
    迁移前已 CREATE TABLE _bak_aud12_20260723 备份原 Float64 数据（可逆性保障）。

引擎选型：
    ReplacingMergeTree(ingest_ts)——ingest_ts 为版本列，财报修正取最新版本。
    PARTITION BY toYYYYMM(report_period) / ORDER BY (symbol, report_period, announce_date)。

审计列（audit 1.7 #ARCH-CH-022）：quality_flag + ingest_ts（兼任版本列）。
"""

from __future__ import annotations

# category_id: fundamental_cashflow_statement
# calc_mode: preload（回测时预加载到内存）

CASHFLOW_STATEMENT_DDL = """
CREATE TABLE IF NOT EXISTS c3_fundamental.cashflow_statement
(
    symbol               String                    COMMENT '证券代码',
    announce_date        Date                      COMMENT '公告日期',
    report_period        Date                      COMMENT '报告期',
    ocf_net              Nullable(Decimal(18,2))   COMMENT '经营活动现金流量净额',
    cash_from_sales      Nullable(Decimal(18,2))   COMMENT '销售商品提供劳务收到的现金',
    ocf_inflow           Nullable(Decimal(18,2))   COMMENT '经营活动现金流入小计',
    ocf_outflow          Nullable(Decimal(18,2))   COMMENT '经营活动现金流出小计',
    icf_net              Nullable(Decimal(18,2))   COMMENT '投资活动现金流量净额',
    icf_inflow           Nullable(Decimal(18,2))   COMMENT '投资活动现金流入小计',
    icf_outflow          Nullable(Decimal(18,2))   COMMENT '投资活动现金流出小计',
    fcf_net              Nullable(Decimal(18,2))   COMMENT '筹资活动现金流量净额',
    fcf_inflow           Nullable(Decimal(18,2))   COMMENT '筹资活动现金流入小计',
    fcf_outflow          Nullable(Decimal(18,2))   COMMENT '筹资活动现金流出小计',
    net_cash_increase    Nullable(Decimal(18,2))   COMMENT '现金及现金等价物净增加额',
    ending_cash_balance  Nullable(Decimal(18,2))   COMMENT '期末现金及现金等价物余额',
    fcff                 Nullable(Decimal(18,2))   COMMENT '公司自由现金流(FCFF)',
    data_source          String                    COMMENT '数据来源',
    quality_flag         UInt8          DEFAULT 1  COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts            DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳(兼任版本列)',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol,'.')>0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(report_period)
ORDER BY (symbol, report_period, announce_date)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "cashflow_statement"
DATABASE = "c3_fundamental"
CATEGORY_ID = "fundamental_cashflow_statement"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree(ingest_ts)"
PARTITION_KEY = "toYYYYMM(report_period)"
ORDER_BY = "(symbol, report_period, announce_date)"

INSERT_COLUMNS = (
    "(symbol, announce_date, report_period, ocf_net, cash_from_sales, ocf_inflow, ocf_outflow, "
    "icf_net, icf_inflow, icf_outflow, fcf_net, fcf_inflow, fcf_outflow, "
    "net_cash_increase, ending_cash_balance, fcff, data_source)"
)
