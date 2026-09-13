# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c3_fundamental_clickhouse.md
# [MODULE] schemas.categories.fundamental.financial_derived
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_financial_derived_ddl.py; build_financial_derived.py;
#             zephyr.data.implementations.financial_derived_compute; zephyr.data.pit_query（白名单）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] financial_derived 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply 脚本执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->verify_schema_truth.py 报漂移+apply_financial_derived_ddl.py --verify 退出码1
# [TESTS] python scripts/ch/apply_financial_derived_ddl.py --verify（建表后）
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""financial_derived（财报派生层）DDL-as-Code（category_id: fund_financial_derived, calc_mode: preload）。

本文件是 c3_fundamental.financial_derived 表结构的唯一真源（DDL-as-Code 模式）。
施工依据：docs/_working/2026-09-12-fundamental-consumption-design.md §M1（消费端 F1-M1，
D2 裁定：statement 粒度不做每日物化——"某天可见什么"是查询语义（pit_query as_of）非存储语义）。

本质（第一性原理）：三大报表是"累计数+多版本"，因子计算要"单季数+TTM+跨表对齐+比率"——
本表把 income/balance/cashflow 三表按 (symbol, report_period) 对齐为 statement 粒度派生宽表，
是 M2 事实侧因子族（FQ-01 应计/GR-01 单季营收/FQ-03 GPOA/FQ-06 F-Score 等）的标准输入。

对齐与 PIT 语义：
    - 衍生行仅在三方同报告期均存在有效公告版本时成行（公告日齐三方可见）。
    - announce_date = 三方公告日最大值（对齐事件=宽表完整可见的最早时点）。
    - 单季/TTM/YoY 引用的历史期数值一律取"衍生公告日时点可见最新版本"
      （修正公告前视免疫，与 pit_query as_of 同构）。

字段分组：
    *_cum / 资产负债字段 = 三表原值宽表（利润/现金流为累计口径，资产负债为时点值）；
    *_q = 单季拆分（累计差分：本期−同年上期，Q1=累计本身）；
    *_yoy/*_qoq = 单季同比/环比增长率（(cur-base)/|base|，基期缺失/为零→NULL）；
    *_ttm = 滚动四季（上年FY+本期累计−去年同季累计；本期为 FY 时=累计本身）；
    比率 = 应计/GPOA/单季毛利率/实际税率/资产负债率（M2 因子族原料）。

引擎选型：
    ReplacingMergeTree(ingest_ts)——同 (symbol, report_period, announce_date) 重建幂等；
    PARTITION BY toYYYYMM(report_period)；ORDER BY (symbol, report_period, announce_date)
    与源表同构（修正公告→同键新版本派生行）。
    审计列对齐 research_report 先例（ingest_ts DateTime64(3,'UTC') + TRAE-082
    MATERIALIZED 派生，表达式与 fundamental_research_report.py 完全一致）。
"""

from __future__ import annotations

# category_id: fund_financial_derived
# calc_mode: preload（回测时预加载到内存）

FINANCIAL_DERIVED_DDL = """
CREATE TABLE IF NOT EXISTS c3_fundamental.financial_derived
(
    symbol         String                   COMMENT '证券代码（6位）',
    report_period  Date                     COMMENT '报告期（季度末）',
    announce_date  Date                     COMMENT '衍生公告日=三方公告日最大值（宽表完整可见时点）',
    revenue_cum    Nullable(Float64)        COMMENT '营业收入（累计）=income.operating_revenue',
    cost_cum       Nullable(Float64)        COMMENT '营业成本（累计）=income.operating_cost',
    operating_profit_cum Nullable(Float64)  COMMENT '营业利润（累计）',
    total_profit_cum Nullable(Float64)      COMMENT '利润总额（累计）',
    income_tax_cum Nullable(Float64)        COMMENT '所得税（累计）',
    np_cum         Nullable(Float64)        COMMENT '净利润含少数股东（累计）=net_profit_incl_minority',
    np_excl_cum    Nullable(Float64)        COMMENT '归母净利润（累计）=net_profit_excl_minority',
    eps_basic      Nullable(Float64)        COMMENT '基本每股收益',
    rd_expense_cum Nullable(Float64)        COMMENT '研发费用（累计）',
    ocf_cum        Nullable(Float64)        COMMENT '经营现金流净额（累计）=cashflow.ocf_net',
    icf_cum        Nullable(Float64)        COMMENT '投资现金流净额（累计）=icf_net',
    fcff_cum       Nullable(Float64)        COMMENT '企业自由现金流=cashflow.fcff',
    total_assets   Nullable(Float64)        COMMENT '总资产（时点）',
    total_liabilities Nullable(Float64)     COMMENT '总负债（时点）',
    total_current_assets Nullable(Float64)  COMMENT '流动资产（时点）',
    total_current_liabilities Nullable(Float64) COMMENT '流动负债（时点）',
    accounts_receivable Nullable(Float64)   COMMENT '应收账款（时点）',
    inventory      Nullable(Float64)        COMMENT '存货（时点）',
    goodwill       Nullable(Float64)        COMMENT '商誉（时点）',
    equity_incl_minority Nullable(Float64)  COMMENT '股东权益含少数股东（时点）',
    retained_earnings Nullable(Float64)     COMMENT '未分配利润（时点）',
    short_term_loan Nullable(Float64)       COMMENT '短期借款（时点）',
    long_term_loan Nullable(Float64)        COMMENT '长期借款（时点）',
    total_shares  Nullable(Float64)         COMMENT '总股本（时点，F-Score 无增发项，v1.1）',
    rev_q          Nullable(Float64)        COMMENT '单季营业收入（累计差分，Q1=累计）',
    cost_q         Nullable(Float64)        COMMENT '单季营业成本',
    np_q           Nullable(Float64)        COMMENT '单季净利润含少数股东',
    ocf_q          Nullable(Float64)        COMMENT '单季经营现金流净额',
    rev_q_yoy      Nullable(Float64)        COMMENT '单季营收同比=(cur-base)/|base|',
    np_q_yoy       Nullable(Float64)        COMMENT '单季净利同比',
    ocf_q_yoy      Nullable(Float64)        COMMENT '单季经营现金流同比',
    rev_q_qoq      Nullable(Float64)        COMMENT '单季营收环比',
    np_q_qoq       Nullable(Float64)        COMMENT '单季净利环比',
    rev_ttm        Nullable(Float64)        COMMENT '营业收入 TTM（滚动四季）',
    cost_ttm       Nullable(Float64)        COMMENT '营业成本 TTM',
    np_ttm         Nullable(Float64)        COMMENT '净利润 TTM',
    ocf_ttm        Nullable(Float64)        COMMENT '经营现金流净额 TTM',
    total_profit_ttm Nullable(Float64)      COMMENT '利润总额 TTM',
    income_tax_ttm Nullable(Float64)        COMMENT '所得税 TTM',
    accrual_ttm    Nullable(Float64)        COMMENT '应计=(np_ttm-ocf_ttm)/total_assets（Sloan 1996，FQ-01 原料）',
    gpoa_ttm       Nullable(Float64)        COMMENT '毛利率/资产=(rev_ttm-cost_ttm)/total_assets（Novy-Marx 2013，FQ-03 原料）',
    gross_margin_q Nullable(Float64)        COMMENT '单季毛利率=(rev_q-cost_q)/rev_q',
    eff_tax_rate_ttm Nullable(Float64)      COMMENT '实际税率=income_tax_ttm/total_profit_ttm（FQ-05 原料）',
    debt_ratio     Nullable(Float64)        COMMENT '资产负债率=total_liabilities/total_assets',
    data_source    LowCardinality(String) DEFAULT 'financial_derived_builder' COMMENT '数据来源（派生层固定值）',
    ingest_ts      DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol,'.')>0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(report_period)
ORDER BY (symbol, report_period, announce_date)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "financial_derived"
DATABASE = "c3_fundamental"
CATEGORY_ID = "fund_financial_derived"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree(ingest_ts)"
PARTITION_KEY = "toYYYYMM(report_period)"
ORDER_BY = "(symbol, report_period, announce_date)"

# 列清单（INSERT 显式指定；排除 MATERIALIZED/DEFAULT(now) 列由 CH 自动填充）
INSERT_COLUMNS = (
    "(symbol, report_period, announce_date, "
    "revenue_cum, cost_cum, operating_profit_cum, total_profit_cum, income_tax_cum, "
    "np_cum, np_excl_cum, eps_basic, rd_expense_cum, "
    "ocf_cum, icf_cum, fcff_cum, "
    "total_assets, total_liabilities, total_current_assets, total_current_liabilities, "
    "accounts_receivable, inventory, goodwill, equity_incl_minority, retained_earnings, "
    "short_term_loan, long_term_loan, total_shares, "
    "rev_q, cost_q, np_q, ocf_q, "
    "rev_q_yoy, np_q_yoy, ocf_q_yoy, rev_q_qoq, np_q_qoq, "
    "rev_ttm, cost_ttm, np_ttm, ocf_ttm, total_profit_ttm, income_tax_ttm, "
    "accrual_ttm, gpoa_ttm, gross_margin_q, eff_tax_rate_ttm, debt_ratio, "
    "data_source)"
)
