# [BLUEPRINT] MOD-BT-082 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] schemas.categories.sim_pocket_daily
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] clickhouse_driver
# [CONSUMERS] scripts/backtest/sim_paper_ledger.py（方案 C 账本模拟钱包日账）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 只增不改（ReplacingMergeTree 按 (strategy_id, trade_date) 去重取最新）；
#   一策略一钱包（strategy_id=钱包键）；金额单位=元
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 执行失败抛异常
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-082 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""sim_pocket_daily 表 DDL——模拟盘方案 C（纯账本模拟）的钱包日账。

一个策略一个虚拟钱包；每日一行（持仓/权益/信号）。资金分档规则与转 sim 流程见
docs/_working/2026-09-14-sim-partition-discussion.md。
"""

from __future__ import annotations

TABLE_NAME = "c1_backtest.sim_pocket_daily"

DDL = """
CREATE TABLE IF NOT EXISTS c1_backtest.sim_pocket_daily
(
    trade_date      Date                  COMMENT '交易日',
    strategy_id     String                COMMENT '钱包键（CAND-xxx / STR-xxx）',
    initial_capital Float64               COMMENT '钱包初始额度（元）',
    cash            Float64               COMMENT '钱包现金余额',
    position_symbol String                COMMENT '持仓标的（纯6位，空=空仓）',
    shares          Float64               COMMENT '持股数',
    position_value  Float64               COMMENT '持仓市值',
    equity          Float64               COMMENT '总权益=cash+position_value',
    daily_pnl       Float64               COMMENT '当日盈亏（元）',
    signal          LowCardinality(String) COMMENT '信号(none/entry/exit/holding/cash)',
    mode            LowCardinality(String) COMMENT 'replay_demo=历史演示/sim_daily=模拟盘正式',
    run_id          String                COMMENT '产生本行的 run/任务标识',
    note            String                COMMENT '备注',
    ingest_ts       DateTime64(3, 'UTC') DEFAULT now('UTC'),
    INDEX idx_sid strategy_id TYPE set(100) GRANULARITY 2
)
ENGINE = ReplacingMergeTree(ingest_ts)
ORDER BY (strategy_id, trade_date)
COMMENT '模拟盘方案C虚拟钱包日账（2026-09-14， Owner 批先C后A）'
"""
