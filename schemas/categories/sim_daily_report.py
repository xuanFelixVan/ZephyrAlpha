# [BLUEPRINT] MOD-BT-223 | docs/03_modules/_domain_backtest/blueprint.md | §模拟盘判定台账
# [MODULE] schemas.categories.sim_daily_report
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] clickhouse_driver
# [CONSUMERS] scripts/backtest/sim_daily_runner.py（plan 桥判定行+结算列回填）；模拟盘日报生成器
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 判定/结算分离铁律：判定列在 asof 落行（只用 ≤T 数据），结算列 T+1 回填
#   （nullable，结算前恒 NULL）；judgment_id 确定性派生（SIMP-<date>-<source>-<subject>），
#   重跑=同键新版本覆盖（ReplacingMergeTree 幂等），非 append 抖动；synthetic 恒 0
#   （全部为真实观测行，观察档仓位=翻译件重放非虚构）
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 执行失败抛异常
# [TESTS] tests/backtest/test_sim_daily_runner.py
# [A_module] module_id=MOD-BT-223 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""sim_daily_report 表 DDL——模拟盘判定台账（日报数据层，判定/结算分离）。

三个 source 平面：plan_bridge（丁线日计划姿态桥）/ e4_replay（E4 观察档翻译件重放）/
platform（平台汇总行）。判定列=当日快照，结算列 T+1 由 settle 回填——与丁线判定台账
四表同款分离语义（forecast ledger 标准 §判定/结算分离铁律），但真源独立于丁域（只读
消费其产物，不写其表）。
设计依据=st-sim-launch-20260922 执行令分包 2/3 + docs/_working/sim_launch/00_campaign_ledger.md §1。
"""

from __future__ import annotations

TABLE_NAME = "c1_backtest.sim_daily_report"

DDL = """
CREATE TABLE IF NOT EXISTS c1_backtest.sim_daily_report
(
    report_date      Date                   COMMENT '台账日（判定基准日 T）',
    source           LowCardinality(String) COMMENT 'plan_bridge/e4_replay/platform',
    subject          String                 COMMENT '对象：index:000300.SH / CAND-xxx / platform',
    judgment_id      String                 COMMENT '确定性派生 SIMP-<date>-<source>-<subject>',
    asof_ts          DateTime64(3, 'UTC')   COMMENT '判定时刻',
    input_cutoff_ts  DateTime64(3, 'UTC')   COMMENT '判定输入截断时刻（PIT）',
    payload          String                 COMMENT '判定快照 JSON（姿态/信号/引用）',
    confidence       Float64                COMMENT '判定置信（plan 桥=plan 行 confidence；重放=1.0）',
    inputs_ref       String                 COMMENT '输入溯源（plan judgment_id/翻译件路径/表）',
    run_id           String                 COMMENT '产生本行的 run/任务标识',
    synthetic        UInt8                  COMMENT '恒 0：真实观测行（禁伪造）',
    realized_scenario Nullable(String)     COMMENT '[结算] 实际归类场景（盘中归类表）',
    realized_value    Nullable(String)      COMMENT '[结算] 实际值 JSON（收益/权益变动/成交数）',
    outcome_ts        Nullable(DateTime64(3, 'UTC')) COMMENT '[结算] 结算时刻',
    eval_method       Nullable(String)      COMMENT '[结算] posture_check/scenario_hit/replay_consistent',
    eval_score        Nullable(Float64)     COMMENT '[结算] 判定命中分（0~1）',
    evaluated_at      Nullable(DateTime64(3, 'UTC')) COMMENT '[结算] 结算落时刻',
    evaluated_by      String                COMMENT '空=未结算；sim_settler=已结算',
    ingest_ts         DateTime64(3, 'UTC') DEFAULT now('UTC'),
    INDEX idx_src source TYPE set(10) GRANULARITY 2
)
ENGINE = ReplacingMergeTree(ingest_ts)
ORDER BY (report_date, source, subject)
COMMENT '模拟盘判定台账（日报数据层，判定/结算分离，2026-09-22 st-sim-launch）'
"""
