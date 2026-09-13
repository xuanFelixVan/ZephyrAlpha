# [BLUEPRINT] MOD-BT-152
# [MODULE] schemas.categories.backtest_hypothesis_precheck
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] none
# [CONSUMERS] 策略工厂 E2 假说预审逻辑门（MOD-BT-091 写）；策略入库线查询（读）
# [STARTUP] imported
# [MATURITY] experimental
# [MODIFY-GUARD] schema-change
# [INVARIANTS] hypothesis_precheck 表 DDL 唯一真源；变更需经 apply DDL 执行；台账只追加不删改；
#   verdict/verdict_reason 由预审管道代码生成（禁 AI 手填）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->scripts/ch/verify_schema_truth.py 报告漂移
# [TESTS] tests/backtest/test_hypothesis_precheck.py
# [A_module] module_id=MOD-BT-152 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""backtest_hypothesis_precheck 表 DDL-as-Code（E2 假说预审判定记录，图9 FAC-E2）。

本文件是 c1_backtest.hypothesis_precheck 表结构的唯一真源（DDL-as-Code 模式）。
预审判定记录台账（每想法每次预审一行），消费者=E2 预审管道（写，MOD-BT-091）/
E3 构造排产（读）/ Owner 审计（读）。

设计决策：
1. MergeTree 台账只追加（同 strategy_screen 同构——同想法可多批重审，历史行全保留）。
2. 库归属 c1_backtest（与 strategy_screen 同库，回测治理产物域）。
3. PARTITION BY toYYYYMM(prechecked_at) 月级分区；ORDER BY (precheck_batch, candidate_id)。
4. 时区铁律（RULE-SCHEMA-TZ / #ARCH-CH-022）：ingest_ts 用 UTC；prechecked_at 用 Asia/Shanghai。
5. verdict 三态（学 strategy_screen screened_in/rejected/deferred_c4 模式）：
   precheck_passed(机制讲得通，放行 E3/E4)/precheck_rejected(讲不通，在此死省算力)/
   precheck_deferred(LLM 不可达/解析失败/低置信，留重跑或人工)。
6. verdict_reason 由预审管道代码生成禁手填（verdict_reason 码体系对齐 R2 语义）：
   pass_mechanism_clear / reject_no_mechanism / reject_lookahead / reject_cost_prohibitive /
   reject_unfalsifiable / reject_tautology / reject_out_of_scope /
   defer_llm_unreachable / defer_parse_fail / defer_low_confidence。
7. birth_channel/birth_batch 从进货台账原样携带（出生证贯穿全链，AI 禁手填）。
"""

from __future__ import annotations

BACKTEST_HYPOTHESIS_PRECHECK_DDL = """
CREATE TABLE IF NOT EXISTS c1_backtest.hypothesis_precheck
(
    ingest_ts         DateTime64(3, 'UTC') DEFAULT now64(3) COMMENT '入库时间(系统列,UTC)',
    precheck_batch    String                  COMMENT '预审批次标识(E2-YYYYMMDD-HHMMSS)',
    candidate_id      String                  COMMENT '候选想法 id(回指进货台账 CAND-*)',
    birth_channel     LowCardinality(String)  COMMENT '出生车道(A-E/human,进货台账原样携带)',
    birth_batch       String                  COMMENT '出生批次(进货台账原样携带)',
    hypothesis_zh     String                  COMMENT '被审假说全文',
    model             String                  COMMENT '预审模型标识(如 qwen3:8b)',
    verdict           LowCardinality(String)  COMMENT '结论(precheck_passed/rejected/deferred)',
    verdict_reason    LowCardinality(String)  COMMENT '理由码(管道代码生成禁手填)',
    confidence        Nullable(Float64)       COMMENT '模型自报置信度(0~1,可空)',
    rationale_zh      String                  COMMENT '判决理由一句话(模型原话截断)',
    latency_ms        Nullable(UInt32)        COMMENT '单次预审耗时毫秒',
    prechecked_at     DateTime64(3, 'Asia/Shanghai') COMMENT '预审结论时间',
    notes             String                  DEFAULT '' COMMENT '备注(AI/人可读)'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(prechecked_at)
ORDER BY (precheck_batch, candidate_id)
"""

TABLE_NAME = "hypothesis_precheck"
DATABASE = "c1_backtest"
CATEGORY_ID = "backtest_hypothesis_precheck"
ENGINE = "MergeTree"
PARTITION_KEY = "toYYYYMM(prechecked_at)"
ORDER_BY = "(precheck_batch, candidate_id)"

INSERT_COLUMNS = (
    "(precheck_batch, candidate_id, birth_channel, birth_batch, hypothesis_zh, model, "
    "verdict, verdict_reason, confidence, rationale_zh, latency_ms, prechecked_at, notes)"
)
