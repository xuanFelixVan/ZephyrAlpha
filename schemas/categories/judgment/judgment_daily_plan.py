# [BLUEPRINT] MOD-L04-001 | docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §三
# [MODULE] schemas.categories.judgment.judgment_daily_plan
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.plan_engine.judgment_ledger(发射器写); zephyr.plan_engine.judgment_settler(结算回填); 作战室任务 3 场景引擎 MOD-PLAN-018(发射)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 表 DDL 唯一真源（自包含禁跨文件 import）；判定列组判定时刻写死；结算列组只许结算器回填；trigger 必须可测量；MergeTree 只增不改；synthetic=1 为合成行
# [MODIFY-GUARD] schema-change
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 与 DB 不一致 -> scripts/ch/verify_schema_truth.py 报告漂移
# [TESTS] tests/plan_engine/test_judgment_ledger.py
# [TTL] permanent
"""judgment_daily_plan 表 DDL-as-Code（判定台账标准 v0.1 表 3 上半）。

作战室任务 3（验证昨日计划）的晨间预案台账：场景引擎（MOD-PLAN-018
场景样本+执行不一致记账）盘前落场景预案，盘中验证事实分表落
judgment_plan_verification（本表只留结算回填的"实际兑现场景"）。

payload JSON 契约（标准 §三表 3）::

    {"scenarios": [{"scenario_id": "S1",
                    "trigger": "open_gap_pct>0.5 AND broker_sector_chg>1.0",
                    "action": "no_chase_wait_pullback", "path_prior": 0.3}, ...],
     "inputs_scope": ["昨收全量", "美股夜盘", "股指期货", "隔夜新闻情绪", "宏观日历"]}

铁律：trigger 必须是可测量表达式——"如果走弱"不合格。发射器按启发式
守卫（trigger 须含比较符或数字）做机械初检，深检归场景引擎。

outcome 结算口径：actual_scenario_id=盘中实际兑现场景（由
judgment_plan_verification 链联结回填）；scenario_brier=path_prior 按
actual one-hot 的多分类 Brier。
"""

from __future__ import annotations

JUDGMENT_DAILY_PLAN_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.judgment_daily_plan
(
    judgment_id String COMMENT '判定唯一 id(ULID 修订=新 id 追加)',
    module_id String COMMENT '产出判定模块(MOD-xxx)',
    model_version String COMMENT '判定算法版本',
    asof_ts DateTime64(3, 'UTC') COMMENT '判定时刻(PIT 锚 UTC)',
    input_cutoff_ts DateTime64(3, 'UTC') COMMENT '数据截断时刻(UTC 且≤asof_ts)',
    horizon String DEFAULT 'intraday_session' COMMENT '预测时段(默认当日盘中)',
    subject String COMMENT '判定对象(index:000300.SH 等)',
    payload String COMMENT '预案内容 JSON(scenarios+inputs_scope)',
    confidence Float64 COMMENT '置信度 [0,1]',
    inputs_ref String DEFAULT '' COMMENT '输入快照指纹/引用清单',
    run_id String DEFAULT '' COMMENT '血缘 run 标识',
    synthetic UInt8 DEFAULT 0 COMMENT '合成/测试行标记(1=合成 冒烟后清理)',
    actual_scenario_id Nullable(String) COMMENT '[结算]实际兑现场景 id(verification 链联结)',
    scenario_brier Nullable(Float64) COMMENT '[结算]path_prior 多分类 Brier(按 actual one-hot)',
    outcome_ts Nullable(DateTime64(3, 'UTC')) COMMENT '[结算]结果时刻(判定器禁写)',
    outcome_value Nullable(String) COMMENT '[结算]结果值 JSON(判定器禁写)',
    eval_method Nullable(String) COMMENT '[结算]结算方法(unresolvable=不可结算)',
    eval_score Nullable(Float64) COMMENT '[结算]结算得分(越小越准)',
    evaluated_at Nullable(DateTime64(3, 'UTC')) COMMENT '[结算]结算时刻(非 NULL=已结算)',
    evaluated_by String DEFAULT 'settlement_agent' COMMENT '[结算]结算写方'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(asof_ts)
ORDER BY (module_id, subject, asof_ts, judgment_id)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "judgment_daily_plan"
DATABASE = "c1_market"
ENGINE = "MergeTree"
CATEGORY_ID = "judgment_daily_plan"

INSERT_COLUMNS = (
    "(judgment_id, module_id, model_version, asof_ts, input_cutoff_ts, horizon, subject,"
    " payload, confidence, inputs_ref, run_id, synthetic)"
)
