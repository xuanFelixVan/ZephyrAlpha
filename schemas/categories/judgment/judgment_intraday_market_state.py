# [BLUEPRINT] MOD-L04-001 | docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §三
# [MODULE] schemas.categories.judgment.judgment_intraday_market_state
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.plan_engine.judgment_ledger(发射器写); zephyr.plan_engine.judgment_settler(结算回填); 作战室任务 1 盘中 L1 跟踪件(发射)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 表 DDL 唯一真源（自包含禁跨文件 import）；判定列组判定时刻写死；结算列组（outcome_*/eval_*/evaluated_*）只许结算器回填；MergeTree 只增不改（修订=新 judgment_id 追加）；synthetic=1 为合成行（冒烟后清理）
# [MODIFY-GUARD] schema-change
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 与 DB 不一致 -> scripts/ch/verify_schema_truth.py 报告漂移
# [TESTS] tests/plan_engine/test_judgment_ledger.py
# [TTL] permanent
"""judgment_intraday_market_state 表 DDL-as-Code（判定台账标准 v0.1 表 1）。

作战室任务 1（盘中实时走势）的判定台账：盘中 L1 跟踪件对大盘状态
（低迷/防御/震荡/进攻/亢奋）的概率判定逐条落库，分钟级。

payload JSON 契约（标准 §三表 1）::

    {"state_label": "震荡",
     "state_probs": {"低迷": 0.1, "防御": 0.1, "震荡": 0.6, "进攻": 0.2, "亢奋": 0.0},
     "evidence": {"volume_ratio": 0.82, "breadth_ratio": 0.41, ...},
     "rest_of_day": {"tail_dir_prob_down": 0.68, "amp_range_pct": [0.2, 0.8]}}

outcome 结算口径（judgment_settler 回填，标准 §四）：
realized_close_vs_open（当日 kline_index close/open-1）为主；
state_realized=±0.3% 带宽三态映射；brier_contrib=多头侧二值 Brier
（p_进攻+p_亢奋 vs up one-hot）；realized_tail_return 需 14:30 分钟源，
Phase 2 接电，当前恒 NULL（不伪造）。

设计决策：
1. MergeTree 只增不改——判定内容不可变，修订=新 judgment_id 追加（标准 §一.3）。
2. 结算列组回填=结算器专属轻量 mutation（WHERE evaluated_at IS NULL 双闸防重复回填），
   判定模块无写通道（铁律 §一.2）。
3. synthetic 列（自裁留痕）：合成/冒烟行标注位，测试夹具口径，清理=DELETE WHERE synthetic=1。
4. 时区铁律（RULE-SCHEMA-TZ）：asof_ts/input_cutoff_ts/outcome_ts/evaluated_at 全部
   DateTime64(3,'UTC') 显式时区。
5. COMMENT 内禁 ASCII 逗号——verify_schema_truth 按顶层逗号切列（防切分误伤）。
"""

from __future__ import annotations

JUDGMENT_INTRADAY_MARKET_STATE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.judgment_intraday_market_state
(
    judgment_id String COMMENT '判定唯一 id(ULID 修订=新 id 追加)',
    module_id String COMMENT '产出判定模块(MOD-xxx)',
    model_version String COMMENT '判定算法版本',
    asof_ts DateTime64(3, 'UTC') COMMENT '判定时刻(PIT 锚 UTC)',
    input_cutoff_ts DateTime64(3, 'UTC') COMMENT '数据截断时刻(UTC 且≤asof_ts)',
    horizon String COMMENT '预测时段(intraday_rest/intraday_session 等)',
    subject String COMMENT '判定对象(index:000300.SH 等)',
    payload String COMMENT '判定内容 JSON(判定时刻写死)',
    confidence Float64 COMMENT '置信度 [0,1]',
    inputs_ref String DEFAULT '' COMMENT '输入快照指纹/引用清单',
    run_id String DEFAULT '' COMMENT '血缘 run 标识',
    synthetic UInt8 DEFAULT 0 COMMENT '合成/测试行标记(1=合成 冒烟后清理)',
    realized_tail_return Nullable(Float64) COMMENT '[结算]尾盘实现收益(14:30 后 Phase 2 接分钟源 当前 NULL)',
    realized_close_vs_open Nullable(Float64) COMMENT '[结算]当日收盘对开盘收益(小数)',
    state_realized Nullable(String) COMMENT '[结算]实现状态(up/flat/down ±0.3% 带宽)',
    brier_contrib Nullable(Float64) COMMENT '[结算]多头侧二值 Brier(p_bull vs up)',
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

TABLE_NAME = "judgment_intraday_market_state"
DATABASE = "c1_market"
ENGINE = "MergeTree"
CATEGORY_ID = "judgment_intraday_market_state"

# 发射器 INSERT 列清单（结算列组禁入——判定器无写通道，铁律 §一.2）
INSERT_COLUMNS = (
    "(judgment_id, module_id, model_version, asof_ts, input_cutoff_ts, horizon, subject,"
    " payload, confidence, inputs_ref, run_id, synthetic)"
)
