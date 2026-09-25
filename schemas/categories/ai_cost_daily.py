# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §obj_s_cost_daily_ddl
# [MODULE] schemas.categories.ai_cost_daily
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] clickhouse_driver
# [CONSUMERS] zephyr.ai_layer.redline.dashboard_pipeline（S5 双指标看板指标 1 数据落点）;
#             scripts/backtest/sim_paper_ledger.py 同族写面先例（幂等替换写）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 只增不改（ReplacingMergeTree 按 (cost_date, channel, cost_source) 去重取最新）；
#   金额单位=元（CNY 口径对齐 config/budget_policy.yaml 预算词汇，不另造预算语义）；
#   cost_source 区分口径来源：bill_api=渠道账单余额/用量 API，telemetry_est=LLM 网关遥测
#   token×registry 单价兜底估算（DESIGN §4 指标 1 数据源分级①②）；
#   DateTime64(3)+显式时区（RULE-SCHEMA-TZ）；库位=c1_backtest（预算/成本族先例
#   alloc_budget_daily 同库位，非回测语义）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_S_perimeter/DESIGN.md §4（DDL 真源正门，
#                变更走 OBJ_R 流水线立案）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 执行失败抛异常（同 schemas/categories 家族先例 sim_pocket_daily）
# [TESTS] tests/ai_layer/redline/test_dashboard_pipeline.py::test_cost_daily_ddl_shape
#         （DDL 形状：库表名/ReplacingMergeTree/ORDER BY/DateTime64(3,'UTC') 显式时区）
# [TTL] permanent
"""ai_cost_daily 表 DDL——AI 层日运行成本日账（OBJ_S 双指标看板指标 1，施工项 S5）。

DESIGN §4 指标 1：日运行成本，数据源按可得性分级——①各渠道账单余额/用量 API（首选）；
②兜底估算=LLM 网关遥测 token 用量×registry 单价；③口径对齐 config/budget_policy.yaml
软/硬限+action_on_exceed 既有词汇。建表走 DDL 真源正门（schemas/categories/），
表创建=运维动作（deploy 批执行 DDL），本文件只锁定形状真源。
"""

from __future__ import annotations

TABLE_NAME = "c1_backtest.ai_cost_daily"

DDL = """
CREATE TABLE IF NOT EXISTS c1_backtest.ai_cost_daily
(
    cost_date      Date                   COMMENT '成本日（UTC 日界）',
    channel        LowCardinality(String) COMMENT '渠道（DEEPSEEK/GLM/OPENROUTER/...）',
    cost_source    LowCardinality(String) COMMENT '口径来源（bill_api=账单API/telemetry_est=遥测兜底估算）',
    cost_amount    Float64                COMMENT '日成本（元）',
    currency       LowCardinality(String) COMMENT '币种（预算口径=CNY）',
    token_input    UInt64                 COMMENT '输入 token（估算口径填遥测值，账单口径可 0）',
    token_output   UInt64                 COMMENT '输出 token（同上）',
    soft_limit_yuan  Float64              COMMENT '落账时的软线快照（元，阈值真源=config/obj_s_degradation.yaml）',
    hard_limit_yuan  Float64              COMMENT '落账时的硬线快照（元，同上）',
    note           String                 COMMENT '备注',
    ingest_ts      DateTime64(3, 'UTC') DEFAULT now('UTC'),
    INDEX idx_ch channel TYPE set(100) GRANULARITY 2
)
ENGINE = ReplacingMergeTree(ingest_ts)
ORDER BY (cost_date, channel, cost_source)
COMMENT 'AI 层日运行成本日账（OBJ_S 双指标看板指标 1，2026-09-23 S5）'
"""
