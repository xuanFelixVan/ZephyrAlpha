# [BLUEPRINT] MOD-PA-CRISIS-GATE-LOG | docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md
# [MODULE] schemas.categories.crisis_gate_log
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.pf_alloc.crisis_gate(写); pipeline_events.run_pf_alloc_daily(L1 接线后写);
#   月度演练 crisis_drill_monthly(读,WO-2c)
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 表 DDL 唯一真源；变更需经 apply DDL 执行；判定行只增不改（MergeTree，禁 UPDATE/DELETE）；
#   每日判定行（多级各写一行合法，按 probe_ts 区分）；state∈{normal,warning,crisis}
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->scripts/ch/verify_schema_truth.py 报告漂移
# [TESTS] tests/pf_alloc/test_crisis_gate.py
# [A_module] module_id=MOD-PA-CRISIS-GATE-LOG | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] crisis-gate-log-ddl-20260918
"""crisis_gate_log 表 DDL-as-Code（WO-2a 危机态三级接线——判定留痕，裁定 D4 新表）。

本文件是 c1_backtest.crisis_gate_log 表结构的唯一真源（DDL-as-Code 模式）。
施工真源：docs/_working/residual_construction/wo2_blackswan_workbook.md §1②/§2
（crisis 状态机动作矩阵 + 危机口径双档裁定 D1）。

定位：危机闸（zephyr.pf_alloc.crisis_gate）每晨判定的可审计事实行——
"今天闸门看见了什么（p_r10/dominant）、判成什么档（state）、三级各动了什么（action_l1/l2/l3）"。
消费者 = L1 管线短路接线方（总统筹）/ 月度演练回看误报率（O1 校准数据源）。

设计决策：
1. MergeTree 只增不改——判定是事实快照，纠错=追加新行（probe_ts 更新者为准），禁改历史。
2. 库归属 c1_backtest（regime_snapshot_history 同库同族：判定器产物，防 c1_market 语义污染）。
3. PARTITION BY toYYYYMM(trade_date) 月级分区——演练按窗口批量读。
4. ORDER BY (trade_date, state)——主读模式=按业务日取当日判定 + 按状态过滤
   （crisis/warning 行回看），同日多级多行并存（追加语义）。
5. 时区铁律（RULE-SCHEMA-TZ / #ARCH-CH-022）：probe_ts/ingest_ts 用 UTC；trade_date 业务日期。
6. action_l1/l2/l3 ∈ {pass, blocked, frozen_new, entry_to_cash, shrinkage_floor, alert_only,
   not_wired, bypass}——自由 String 不设枚举约束（留演化空间），口径由 crisis_gate 模块注释维护。
"""

from __future__ import annotations

CRISIS_GATE_LOG_DDL = """
CREATE TABLE IF NOT EXISTS c1_backtest.crisis_gate_log
(
    ingest_ts  DateTime64(3, 'UTC') DEFAULT now64(3) COMMENT '入库时间(系统列,UTC)',
    probe_ts   DateTime64(3, 'UTC')                  COMMENT '判定探针时刻(UTC, crisis_gate 判定瞬间)',
    trade_date Date                                   COMMENT '业务交易日(判定所依据的业务日,PIT 口径)',
    state      LowCardinality(String)                 COMMENT '判定档位: normal|warning|crisis',
    p_r10      Float64                                COMMENT 'regime overlay CRISIS 态概率(0..1)',
    dominant   LowCardinality(String)                 COMMENT 'regime 快照 dominant 态键(r1..r4,r10..r12,unknown)',
    action_l1  LowCardinality(String)                 COMMENT 'L1 管线级动作: pass|blocked|not_wired|bypass',
    action_l2  LowCardinality(String)                 COMMENT 'L2 裁决级动作: pass|frozen_new|shrinkage_floor|alert_only|bypass',
    action_l3  LowCardinality(String)                 COMMENT 'L3 账本级动作: pass|entry_to_cash|not_applicable|bypass'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, state)
"""

# 表元数据
TABLE_NAME = "crisis_gate_log"
DATABASE = "c1_backtest"
CATEGORY_ID = "crisis_gate_log"
CALC_MODE = "batch"
ENGINE = "MergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(trade_date, state)"

# 库表限定名（消费方 SQL 拼接唯一口径）
QUALIFIED_NAME = f"{DATABASE}.{TABLE_NAME}"

# 列清单（用于 INSERT；ingest_ts 系统列 DEFAULT 不入 INSERT）
INSERT_COLUMNS = "(probe_ts, trade_date, state, p_r10, dominant, action_l1, action_l2, action_l3)"

# action 列口径词表（模块级注释真源，非 DB 约束）
ACTION_L1_PASS = "pass"
ACTION_L1_BLOCKED = "blocked"
ACTION_L1_NOT_WIRED = "not_wired"
ACTION_L2_FROZEN_NEW = "frozen_new"
ACTION_L2_SHRINKAGE_FLOOR = "shrinkage_floor"
ACTION_L2_ALERT_ONLY = "alert_only"
ACTION_L3_ENTRY_TO_CASH = "entry_to_cash"
ACTION_BYPASS = "bypass"
