# [BLUEPRINT] MOD-L04-001 | docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §三
# [MODULE] schemas.categories.judgment.judgment_plan_verification
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.plan_engine.judgment_settler(结算联结回填 judgment_daily_plan); 作战室任务 3 执行不一致记账(对接)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 表 DDL 唯一真源（自包含禁跨文件 import）；只增不改（验证事实追加）；每行经 plan_judgment_id 联结 judgment_daily_plan；synthetic=1 为合成行
# [MODIFY-GUARD] schema-change
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 与 DB 不一致 -> scripts/ch/verify_schema_truth.py 报告漂移
# [TESTS] tests/plan_engine/test_judgment_ledger.py
# [TTL] permanent
"""judgment_plan_verification 表 DDL-as-Code（判定台账标准 v0.1 表 3 下半）。

晨间预案（judgment_daily_plan）的盘中验证事实表：场景触发命中、实际
兑现场景、执行是否跟随预案、执行偏差清单、预案质量分。与 daily_plan
分表（2026-09-16 施工令：plan 与 verification 分开两表）——验证事实
是盘中追加的独立事件流，不是预案行的可变列。

行契约：每行经 plan_judgment_id 联结一条预案判定；同 plan 多次验证
（盘中多时点）=多行追加（只增不改）。写方=作战室执行链/结算器联结通道，
verified_by 留痕。对接既有"执行不一致"记账（MOD-PLAN-018 侧）。

scenario_hits JSON 契约::

    [{"scenario_id": "S2", "trigger_ts": "2026-09-16 10:05:00.000",
      "trigger_price": 3987.45}, ...]
"""

from __future__ import annotations

JUDGMENT_PLAN_VERIFICATION_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.judgment_plan_verification
(
    verification_id String COMMENT '验证行唯一 id(ULID)',
    plan_judgment_id String COMMENT '关联预案判定(judgment_daily_plan.judgment_id)',
    scenario_hits String DEFAULT '[]' COMMENT '触发场景 JSON 数组 [{scenario_id/trigger_ts/trigger_price}]',
    actual_scenario_id String DEFAULT '' COMMENT '实际兑现场景 id(空=无场景触发)',
    plan_followed UInt8 DEFAULT 0 COMMENT '执行是否跟随预案(0/1)',
    deviations String DEFAULT '[]' COMMENT '执行偏差 JSON 数组(对接执行不一致记账)',
    plan_quality_score Nullable(Float64) COMMENT '预案质量分 [0,1]',
    verified_at DateTime64(3, 'UTC') COMMENT '验证时刻(UTC)',
    verified_by String DEFAULT 'settlement_agent' COMMENT '验证写方',
    synthetic UInt8 DEFAULT 0 COMMENT '合成/测试行标记(1=合成 冒烟后清理)'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(verified_at)
ORDER BY (plan_judgment_id, verified_at, verification_id)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "judgment_plan_verification"
DATABASE = "c1_market"
ENGINE = "MergeTree"
CATEGORY_ID = "judgment_plan_verification"

INSERT_COLUMNS = (
    "(verification_id, plan_judgment_id, scenario_hits, actual_scenario_id,"
    " plan_followed, deviations, plan_quality_score, verified_at, verified_by, synthetic)"
)
