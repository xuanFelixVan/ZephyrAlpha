# [BLUEPRINT] MOD-BT-085 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] schemas.categories.sim_trade_log
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] clickhouse_driver
# [CONSUMERS] scripts/backtest/sim_paper_ledger.py（事件写入+账本重建）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 事件溯源唯一真源（sim_pocket_daily 快照由本表推导，可全量重建）；
#   ReplacingMergeTree 按 (strategy_id, trade_date, action) 幂等
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 执行失败抛异常
# [TESTS] tests/backtest/test_sim_paper_ledger.py
# [A_module] module_id=MOD-BT-131 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""sim_trade_log 表 DDL——模拟盘成交事件流水（事件溯源唯一真源）。

每笔虚拟成交一行（entry/exit），signal_reason 记触发判据快照供 AI 复核；
sim_pocket_daily 日快照由本事件流推导，账本损毁可全量重建（后备方案技术底座）。
设计依据=docs/_working/2026-09-14-sim-platform-blueprint.md 批 1。
"""

from __future__ import annotations

TABLE_NAME = "c1_backtest.sim_trade_log"

DDL = """
CREATE TABLE IF NOT EXISTS c1_backtest.sim_trade_log
(
    trade_date      Date                   COMMENT '成交日',
    strategy_id     String                 COMMENT '钱包键',
    symbol          String                 COMMENT '标的（纯6位）',
    action          LowCardinality(String) COMMENT 'entry/exit',
    shares          Float64                COMMENT '成交股数',
    price           Float64                COMMENT '成交价（方案C=收盘价）',
    cost_paid       Float64                COMMENT '本次交易成本（元）',
    cash_after      Float64                COMMENT '事件后钱包现金',
    signal_reason   String                 COMMENT '触发判据快照（供 AI 复核）',
    mode            LowCardinality(String) COMMENT 'replay_demo/sim_daily',
    run_id          String                 COMMENT '产生本事件的 run/任务标识',
    ingest_ts       DateTime64(3, 'UTC') DEFAULT now('UTC'),
    INDEX idx_sid strategy_id TYPE set(100) GRANULARITY 2
)
ENGINE = ReplacingMergeTree(ingest_ts)
ORDER BY (strategy_id, trade_date, action)
COMMENT '模拟盘成交事件流水（事件溯源唯一真源，2026-09-14 平台蓝图批1）'
"""
