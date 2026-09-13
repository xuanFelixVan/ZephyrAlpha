# [BLUEPRINT] MOD-BT-088 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] schemas.categories.sim_platform_journal
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] clickhouse_driver
# [CONSUMERS] scripts/backtest/sim_platform_journal.py（平台日刊）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 一交易日一行（平台级汇总）；ReplacingMergeTree 按 trade_date 幂等；
#   anomalies 为 JSON 数组字符串（每项=一条异常描述）；degraded=1 表示当日存在异常
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 执行失败抛异常
# [TESTS] tests/backtest/test_sim_platform_journal.py
# [A_module] module_id=MOD-BT-088 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""sim_platform_journal 表 DDL——模拟盘平台日刊（每日全盘汇总+健康度）。

回答 Owner"整个模拟盘的日志"：每日一行，记录全钱包汇总/事件数/数据新鲜度/心跳/异常清单。
设计依据=docs/_working/2026-09-14-sim-platform-blueprint.md 批 2。
"""

from __future__ import annotations

TABLE_NAME = "c1_backtest.sim_platform_journal"

DDL = """
CREATE TABLE IF NOT EXISTS c1_backtest.sim_platform_journal
(
    trade_date         Date                   COMMENT '交易日',
    pocket_count       UInt16                 COMMENT '活跃钱包数',
    total_equity       Float64                COMMENT '全平台总权益（元）',
    pockets_summary    String                 COMMENT '各钱包权益 JSON（{strategy_id: equity}）',
    event_count        UInt16                 COMMENT '当日成交事件数',
    data_freshness_ok  UInt8                  COMMENT '行情数据新鲜度（1=行情表 max_date>=当日）',
    heartbeat_ok       UInt8                  COMMENT '账本心跳（1=每个活跃钱包当日均有行）',
    anomalies          String                 COMMENT '异常清单（JSON 数组，空=无）',
    degraded           UInt8                  COMMENT '降级标记（1=当日存在异常）',
    run_id             String                 COMMENT '产生本行的任务标识',
    note               String                 COMMENT '备注',
    ingest_ts          DateTime64(3, 'UTC') DEFAULT now('UTC')
)
ENGINE = ReplacingMergeTree(ingest_ts)
ORDER BY trade_date
COMMENT '模拟盘平台日刊（2026-09-14 平台蓝图批2）'
"""
