# [BLUEPRINT] MOD-ALT-012 | docs/_working/infoaxis/12_research_workbook.md §2
# [MODULE] schemas.categories.fundamental.expectation_revision_daily
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.alt_data.expectation_revision_assembler (写，写侧唯一); 九阶段选票漏斗（读，二期）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] DDL 唯一真源；一行=某业务日某标的一致预期修正三件套读数（ReplacingMergeTree
#   同日刷新幂等）；口径语义=expectations.py exp02/03/05（注释互指不复制公式）；分母保护
#   max(n_orgs,1)＋近零 |eps|<1e-6 跳过（与 PEAD 同口径）；DateTime64(3)+显式时区
# [MODIFY-GUARD] schema-change
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] verify_schema_truth.py 报告漂移
# [TESTS] tests/alt_data/test_expectation_revision_assembler.py
# [A_module] module_id=MOD-ALT-012 | layer=schema | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] mod-alt-012-expectation-revision-daily-20261014
"""expectation_revision_daily 表 DDL-as-Code——一致预期修正三件套（P2 研报首刀）。"""

from __future__ import annotations

TABLE_NAME = "c3_fundamental.expectation_revision_daily"
DATABASE = "c3_fundamental"
EXPECTATION_REVISION_DAILY_DDL = """
CREATE TABLE IF NOT EXISTS c3_fundamental.expectation_revision_daily
(
    trade_date         Date                            COMMENT '业务日T(装配批)',
    symbol             LowCardinality(String)          COMMENT '标的代码',
    eps_consensus      Float64                         COMMENT '当日一致预期EPS(consensus_daily)',
    eps_prior          Float64                         COMMENT '先窗(约20交易日前)一致预期EPS',
    revision_momentum  Float64                         COMMENT '修正动量=(now-prior)/|prior|(exp02 语义)',
    revision_breadth   Float64                         COMMENT '修正宽度=(n_buy+n_add-n_negative)/max(n_orgs,1)(exp03 语义)',
    dispersion         Nullable(Float64)               COMMENT '离散度=eps_std/|eps_consensus|(exp05 语义;近零跳过=NULL)',
    n_orgs             Int32                           COMMENT '覆盖机构数',
    detail             String               DEFAULT '' COMMENT '明细',
    ingest_ts          DateTime64(3, 'UTC') DEFAULT now64(3) COMMENT '入库时间(DB 侧生成;RULE-SCHEMA-TZ)'
)
ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, symbol)
COMMENT '一致预期修正三件套(st-infoaxis P2 研报首刀:consensus_daily 683万行装配为信号面)'
"""
DDL = EXPECTATION_REVISION_DAILY_DDL
INSERT_COLUMNS = (
    "trade_date",
    "symbol",
    "eps_consensus",
    "eps_prior",
    "revision_momentum",
    "revision_breadth",
    "dispersion",
    "n_orgs",
    "detail",
)
