# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.fundamental_balance_sheet
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_fundamental_tables_ddl; zephyr.data.implementations.miniqmt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] balance_sheet 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->apply_fundamental_tables_ddl.py --verify退出码1
# [TESTS] scripts/ch/apply_fundamental_tables_ddl.py --verify (smoke test)
# [TTL] permanent
"""balance_sheet（资产负债表）DDL-as-Code（category_id: fundamental_balance_sheet, calc_mode: preload）。

本文件是 c3_fundamental.balance_sheet 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

精度裁定（audit 1.2 #ARCH-CH-026，2026-07-23 治本）：
    金额字段由 Float64 迁移至 Nullable(Decimal(18,2))——消除二进制浮点精度隐患。
    max 总资产 5.6T < Decimal(18,2) 上限 10^16 安全。
    total_shares（总股本）保留 Nullable(Float64)——股本数量非金额字段，
    不在 audit 1.2（金额/价格精度）范围内；如需精确计数可后续迁移至 Decimal(18,0)。
    迁移前已 CREATE TABLE _bak_aud12_20260723 备份原 Float64 数据（可逆性保障）。

引擎选型：
    ReplacingMergeTree(ingest_ts)——ingest_ts 为版本列，财报修正取最新版本。
    PARTITION BY toYYYYMM(report_period) / ORDER BY (symbol, report_period, announce_date)。

审计列（audit 1.7 #ARCH-CH-022）：quality_flag + ingest_ts（兼任版本列）。
"""

from __future__ import annotations

# category_id: fundamental_balance_sheet
# calc_mode: preload（回测时预加载到内存）

BALANCE_SHEET_DDL = """
CREATE TABLE IF NOT EXISTS c3_fundamental.balance_sheet
(
    symbol                       String                    COMMENT '证券代码',
    announce_date                Date                      COMMENT '公告日期',
    report_period                Date                      COMMENT '报告期',
    company_type                 Nullable(String)          COMMENT '公司类型',
    total_shares                 Nullable(Float64)         COMMENT '总股本(股,数量非金额)',
    monetary_capital             Nullable(Decimal(18,2))   COMMENT '货币资金',
    accounts_receivable          Nullable(Decimal(18,2))   COMMENT '应收账款',
    inventory                    Nullable(Decimal(18,2))   COMMENT '存货',
    total_current_assets         Nullable(Decimal(18,2))   COMMENT '流动资产合计',
    fixed_assets                 Nullable(Decimal(18,2))   COMMENT '固定资产',
    intangible_assets            Nullable(Decimal(18,2))   COMMENT '无形资产',
    goodwill                     Nullable(Decimal(18,2))   COMMENT '商誉',
    total_non_current_assets     Nullable(Decimal(18,2))   COMMENT '非流动资产合计',
    total_assets                 Nullable(Decimal(18,2))   COMMENT '资产总计',
    short_term_loan              Nullable(Decimal(18,2))   COMMENT '短期借款',
    long_term_loan               Nullable(Decimal(18,2))   COMMENT '长期借款',
    accounts_payable             Nullable(Decimal(18,2))   COMMENT '应付账款',
    total_current_liabilities    Nullable(Decimal(18,2))   COMMENT '流动负债合计',
    total_non_current_liabilities Nullable(Decimal(18,2))  COMMENT '非流动负债合计',
    total_liabilities            Nullable(Decimal(18,2))   COMMENT '负债合计',
    equity_excl_minority         Nullable(Decimal(18,2))   COMMENT '所有者权益(不含少数股东)',
    equity_incl_minority         Nullable(Decimal(18,2))   COMMENT '所有者权益(含少数股东)',
    capital_reserve              Nullable(Decimal(18,2))   COMMENT '资本公积',
    retained_earnings            Nullable(Decimal(18,2))   COMMENT '盈余公积',
    surplus_reserve              Nullable(Decimal(18,2))   COMMENT '未分配利润',
    data_source                  String                    COMMENT '数据来源',
    quality_flag                 UInt8          DEFAULT 1  COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts                    DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳(兼任版本列)',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol,'.')>0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(report_period)
ORDER BY (symbol, report_period, announce_date)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "balance_sheet"
DATABASE = "c3_fundamental"
CATEGORY_ID = "fundamental_balance_sheet"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree(ingest_ts)"
PARTITION_KEY = "toYYYYMM(report_period)"
ORDER_BY = "(symbol, report_period, announce_date)"

INSERT_COLUMNS = (
    "(symbol, announce_date, report_period, company_type, total_shares, "
    "monetary_capital, accounts_receivable, inventory, total_current_assets, fixed_assets, "
    "intangible_assets, goodwill, total_non_current_assets, total_assets, short_term_loan, "
    "long_term_loan, accounts_payable, total_current_liabilities, total_non_current_liabilities, "
    "total_liabilities, equity_excl_minority, equity_incl_minority, capital_reserve, "
    "retained_earnings, surplus_reserve, data_source)"
)
