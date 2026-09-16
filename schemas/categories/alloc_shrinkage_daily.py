# [BLUEPRINT] MOD-PA-041 | docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md
# [MODULE] schemas.categories.alloc_shrinkage_daily
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.pf_alloc.allocation_persistence(写); 分配对账/regime 供给链对表(读)
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 表 DDL 唯一真源（DDL-as-Code）；只增不改（重跑=新 run_id 追加）；
#   一行=某 run 某交易日的**全局** Shrinkage 明细（Shrinkage 是全局的，一态一值，所有策略共用——
#   MOD-PA-007 §3.1 实现注记），故本表 grain=（trade_date, run_id），不含 strategy_id；
#   global_shrinkage≤1.0 只减不增；unallocated_cash=组合总资金×(1−Σeffective_budget)≥0
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 与 DB 不一致→scripts/ch/verify_schema_truth.py 报告漂移
# [TESTS] tests/pf_alloc/test_pf_alloc_schemas.py
# [A_module] module_id=MOD-PA-041 | layer=schema | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] alloc-shrinkage-daily-mod-pa-041-20260916
"""alloc_shrinkage_daily 表 DDL-as-Code——全局 Shrinkage 节流与总暴露落地表。

真源：pf_alloc_consumer_mining PFA-2（全 CH 无 alloc/budget/shrinkage 表）+ PFA-3
（regime/Shrinkage 在实盘分配里零消费，"实盘连被压缩的分配器都没有"）。

定位：MOD-PA-007 ShrinkageDetail + 组合级总暴露的可对账落地面。每分配周期一行：
ConfidenceSignal（regime max(P) 四档）× RiskSignal（13 参数聚合）→ global_shrinkage，
并登记与 regime_snapshot_history 快照 Shrinkage 的偏差（回测/实盘同源性对表，PFA-5 治本输入）。

设计决策：
1. grain=(trade_date, run_id)——Shrinkage 是全局量（一个 regime 态一个值，所有策略共用），
   与 alloc_budget_daily（grain 含 strategy_id）分层，避免同值冗余 N 行。
2. regime_source_* 列 = 分配的 regime 输入溯源（哪次印教材 run 的哪一天、滞后几天），
   使"实盘消费的是哪份教材"可判（PFA-3 的可观测面）。
3. risk_signal_source 枚举 = RiskSignal 的三条来源口径显式登记：
   snapshot_direct（教材 risk_signal 列直取）/ snapshot_decomposed（教材 EMA Shrinkage ÷
   当日 ConfidenceSignal 档值反演，教材分量列缺席时的 PIT 近似）/ neutral_fail_closed
   （无教材可用→概率向量退化为平坦分布→ConfidenceSignal 落最低档 0.30，节流不为零）。
4. 时区铁律：ingest_ts=DateTime64(3,'UTC') DEFAULT now64(3)（DB 侧生成，写侧生成器禁 datetime.now()）。
"""

from __future__ import annotations

TABLE_NAME = "c1_backtest.alloc_shrinkage_daily"
DDL = """
CREATE TABLE IF NOT EXISTS c1_backtest.alloc_shrinkage_daily
(
    ingest_ts               DateTime64(3, 'UTC') DEFAULT now64(3) COMMENT '入库时间(系统列,UTC,DB侧生成)',
    run_id                  String               COMMENT '分配 run 标识(与 alloc_budget_daily 同 run_id 对账)',
    trade_date              Date                 COMMENT '业务交易日',
    regime_source_run_id    String               COMMENT 'regime 输入来源 run(印教材 run_id / synthetic_fail_closed)',
    regime_source_date      Date                 COMMENT 'regime 输入 as-of 日(PIT：≤trade_date 的最近快照)',
    regime_lag_days         Int32                COMMENT '教材滞后天数(trade_date − regime_source_date)',
    dominant                LowCardinality(String) COMMENT 'max(P) 对应态 r1..r4/r10..r12 / unknown',
    max_probability         Float64              COMMENT 'max(P) 即 ConfidenceSignal 四档映射输入',
    confidence_signal       Float64              COMMENT 'ConfidenceSignal∈{0.30,0.60,0.85,1.00}',
    risk_signal             Float64              COMMENT 'RiskSignal 13 参数聚合值∈[0.30,1.00]',
    raw_shrinkage           Float64              COMMENT 'confidence×risk(裁剪前)',
    global_shrinkage        Float64              COMMENT 'final_shrinkage=global_shrinkage∈[0.05,1.0] 只减不增',
    shrinkage_enabled       UInt8                COMMENT 'C1 验证开关(1=节流生效/0=恒 1.0)',
    is_crisis               UInt8                COMMENT 'CRISIS overlay 态(floor 0.09→0.05)',
    risk_signal_source      LowCardinality(String) COMMENT 'snapshot_direct|snapshot_decomposed|neutral_fail_closed',
    snapshot_shrinkage      Float64              COMMENT 'regime_snapshot_history 快照 Shrinkage(EMA 后)，无教材=NaN',
    delta_vs_snapshot       Float64              COMMENT 'global_shrinkage − snapshot_shrinkage(回测/实盘同源性对账)',
    portfolio_total_capital Float64              COMMENT '组合总资金(元)',
    sum_effective_budget    Float64              COMMENT 'Σ effective_budget(=global_shrinkage×Σcold_started_allocation≤1.0)',
    unallocated_cash        Float64              COMMENT '未分配预备金(元)=total×(1−Σeffective)≥0',
    probs_json              String               COMMENT 'regime 概率向量 JSON(含来源与 schema_version)',
    schema_version          LowCardinality(String) COMMENT '行契约版本'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, run_id)
COMMENT '组合分配链全局 Shrinkage 节流与总暴露落地表（车道 D 实盘接线，2026-09-16）'
"""

DATABASE = "c1_backtest"
CATEGORY_ID = "alloc_shrinkage_daily"
CALC_MODE = "batch"
ENGINE = "MergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(trade_date, run_id)"

INSERT_COLUMNS = (
    "(run_id, trade_date, regime_source_run_id, regime_source_date, regime_lag_days,"
    " dominant, max_probability, confidence_signal, risk_signal, raw_shrinkage,"
    " global_shrinkage, shrinkage_enabled, is_crisis, risk_signal_source,"
    " snapshot_shrinkage, delta_vs_snapshot, portfolio_total_capital, sum_effective_budget,"
    " unallocated_cash, probs_json, schema_version)"
)

# 读侧查询模板（{table}/{date} 占位符约定同 alloc_budget_daily）
SQL_LATEST_REGIME_SNAPSHOT = (
    "SELECT run_id, trade_date, p_r1, p_r2, p_r3, p_r4, p_r10, p_r11, p_r12, dominant, "
    "confidence, confidence_signal, risk_signal, shrinkage, probs_json "
    "FROM {table} WHERE trade_date <= '{date}' "
    "ORDER BY trade_date DESC, run_id DESC LIMIT 1"
)
