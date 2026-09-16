# [BLUEPRINT] MOD-L04-001 | docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §三
# [MODULE] schemas.categories.judgment.judgment_next_day_forecast
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.plan_engine.judgment_ledger(发射器写); zephyr.plan_engine.judgment_settler(结算回填); 作战室任务 2 盘后概率件(发射)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 表 DDL 唯一真源（自包含禁跨文件 import）；判定列组判定时刻写死；结算列组只许结算器回填；MergeTree 只增不改；synthetic=1 为合成行
# [MODIFY-GUARD] schema-change
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 与 DB 不一致 -> scripts/ch/verify_schema_truth.py 报告漂移
# [TESTS] tests/plan_engine/test_judgment_ledger.py
# [TTL] permanent
"""judgment_next_day_forecast 表 DDL-as-Code（判定台账标准 v0.1 表 2）。

作战室任务 2（明日概率）的判定台账：T 日盘后概率件对 T+1 的三元分布
（p_up/p_flat/p_down）+ 分位数判定落库，T+1 收盘后由结算器回填。

payload JSON 契约（标准 §三表 2）::

    {"p_up": 0.35, "p_flat": 0.25, "p_down": 0.40,
     "quantiles": {"q10": -1.2, "q25": -0.5, "q50": 0.05, "q75": 0.6, "q90": 1.3},
     "expected_vol_pct": 0.9, "expected_range_pct": 1.4}

outcome 结算口径（T+1 收盘回填）：realized_return=kline_index(000300)
T+1 close/T close-1；realized_label=±0.1% 带宽三态；brier_score=三元
分布多分类 Brier；log_loss=-ln(p[实际标签])；calibration_bucket=p_up
十分位桶（reliability curve 数据源）。

设计决策同 judgment_intraday_market_state（MergeTree 只增不改/结算列组
结算器专属/synthetic 合成标记/UTC 显式时区/COMMENT 禁 ASCII 逗号）。
"""

from __future__ import annotations

JUDGMENT_NEXT_DAY_FORECAST_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.judgment_next_day_forecast
(
    judgment_id String COMMENT '判定唯一 id(ULID 修订=新 id 追加)',
    module_id String COMMENT '产出判定模块(MOD-xxx)',
    model_version String COMMENT '判定算法版本',
    asof_ts DateTime64(3, 'UTC') COMMENT '判定时刻(PIT 锚 UTC)',
    input_cutoff_ts DateTime64(3, 'UTC') COMMENT '数据截断时刻(UTC 且≤asof_ts)',
    horizon String DEFAULT 'next_day' COMMENT '预测时段(默认 next_day)',
    subject String COMMENT '判定对象(index:000300.SH 等)',
    payload String COMMENT '判定内容 JSON(判定时刻写死)',
    confidence Float64 COMMENT '置信度 [0,1]',
    inputs_ref String DEFAULT '' COMMENT '输入快照指纹/引用清单',
    run_id String DEFAULT '' COMMENT '血缘 run 标识',
    synthetic UInt8 DEFAULT 0 COMMENT '合成/测试行标记(1=合成 冒烟后清理)',
    realized_return Nullable(Float64) COMMENT '[结算]T+1 收盘对 T 收盘收益(小数)',
    realized_label Nullable(String) COMMENT '[结算]T+1 实现标签(up/flat/down ±0.1% 带宽)',
    brier_score Nullable(Float64) COMMENT '[结算]三元分布多分类 Brier',
    log_loss Nullable(Float64) COMMENT '[结算]-ln(p[实际标签])',
    calibration_bucket Nullable(String) COMMENT '[结算]p_up 十分位桶(如 0.3-0.4)',
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

TABLE_NAME = "judgment_next_day_forecast"
DATABASE = "c1_market"
ENGINE = "MergeTree"
CATEGORY_ID = "judgment_next_day_forecast"

INSERT_COLUMNS = (
    "(judgment_id, module_id, model_version, asof_ts, input_cutoff_ts, horizon, subject,"
    " payload, confidence, inputs_ref, run_id, synthetic)"
)
