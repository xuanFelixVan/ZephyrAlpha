# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.fundamental_income_statement
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_fundamental_tables_ddl; zephyr.data.implementations.miniqmt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] income_statement 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->apply_fundamental_tables_ddl.py --verify退出码1
# [TESTS] scripts/ch/apply_fundamental_tables_ddl.py --verify (smoke test)
# [TTL] permanent
"""income_statement（利润表）DDL-as-Code（category_id: fundamental_income_statement, calc_mode: preload）。

本文件是 c3_fundamental.income_statement 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

精度裁定（audit 1.2 #ARCH-CH-026，2026-07-23 治本）：
    金额字段由 Float64 迁移至 Nullable(Decimal(18,2))——消除二进制浮点精度隐患，
    与行情表 amount Decimal(18,2) 口径一致；max 营收 3.3T < Decimal(18,2) 上限 10^16 安全。
    EPS 字段迁移至 Nullable(Decimal(18,4))——每股收益需 4 位小数精度。
    迁移前已 CREATE TABLE _bak_aud12_20260723 备份原 Float64 数据（可逆性保障）。

引擎选型：
    ReplacingMergeTree(ingest_ts)——ingest_ts 为版本列，重复行按入库时间保留最新，
    适配财报修正场景（同一 report_period 多次披露，取最新版本，配合 PIT 查询防前视偏差）。
    PARTITION BY toYYYYMM(report_period)——按报告期月分区，支持整分区归档。
    ORDER BY (symbol, report_period, announce_date)——单标的多报告期点查友好。

审计列（audit 1.7 #ARCH-CH-022）：
    quality_flag UInt8 DEFAULT 1 + ingest_ts DateTime DEFAULT now()。
    ingest_ts 兼任版本列（ReplacingMergeTree(ingest_ts)）。
"""

from __future__ import annotations

# category_id: fundamental_income_statement
# calc_mode: preload（回测时预加载到内存）

INCOME_STATEMENT_DDL = """
CREATE TABLE IF NOT EXISTS c3_fundamental.income_statement
(
    symbol                   String                    COMMENT '证券代码',
    announce_date            Date                      COMMENT '公告日期',
    actual_announce_date     Date                      COMMENT '实际公告日期',
    report_period            Date                      COMMENT '报告期',
    company_type             Nullable(String)          COMMENT '公司类型',
    total_revenue            Nullable(Decimal(18,2))   COMMENT '营业总收入',
    operating_revenue        Nullable(Decimal(18,2))   COMMENT '营业收入',
    total_cost               Nullable(Decimal(18,2))   COMMENT '营业总成本',
    operating_cost           Nullable(Decimal(18,2))   COMMENT '营业成本',
    tax_surcharge            Nullable(Decimal(18,2))   COMMENT '税金及附加',
    selling_expense          Nullable(Decimal(18,2))   COMMENT '销售费用',
    admin_expense            Nullable(Decimal(18,2))   COMMENT '管理费用',
    financial_expense        Nullable(Decimal(18,2))   COMMENT '财务费用',
    rd_expense               Nullable(Decimal(18,2))   COMMENT '研发费用',
    operating_profit         Nullable(Decimal(18,2))   COMMENT '营业利润',
    non_op_income            Nullable(Decimal(18,2))   COMMENT '营业外收入',
    non_op_expense           Nullable(Decimal(18,2))   COMMENT '营业外支出',
    total_profit             Nullable(Decimal(18,2))   COMMENT '利润总额',
    income_tax               Nullable(Decimal(18,2))   COMMENT '所得税费用',
    net_profit_incl_minority Nullable(Decimal(18,2))   COMMENT '净利润(含少数股东损益)',
    net_profit_excl_minority Nullable(Decimal(18,2))   COMMENT '净利润(不含少数股东损益)',
    minority_interest        Nullable(Decimal(18,2))   COMMENT '少数股东损益',
    eps_basic                Nullable(Decimal(18,4))   COMMENT '基本每股收益',
    eps_diluted              Nullable(Decimal(18,4))   COMMENT '稀释每股收益',
    comprehensive_income     Nullable(Decimal(18,2))   COMMENT '综合收益总额',
    data_source              String                    COMMENT '数据来源',
    quality_flag             UInt8          DEFAULT 1  COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts                DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳(兼任版本列)',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol,'.')>0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(report_period)
ORDER BY (symbol, report_period, announce_date)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "income_statement"
DATABASE = "c3_fundamental"
CATEGORY_ID = "fundamental_income_statement"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree(ingest_ts)"
PARTITION_KEY = "toYYYYMM(report_period)"
ORDER_BY = "(symbol, report_period, announce_date)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
INSERT_COLUMNS = (
    "(symbol, announce_date, actual_announce_date, report_period, company_type, "
    "total_revenue, operating_revenue, total_cost, operating_cost, tax_surcharge, "
    "selling_expense, admin_expense, financial_expense, rd_expense, operating_profit, "
    "non_op_income, non_op_expense, total_profit, income_tax, net_profit_incl_minority, "
    "net_profit_excl_minority, minority_interest, eps_basic, eps_diluted, "
    "comprehensive_income, data_source)"
)
