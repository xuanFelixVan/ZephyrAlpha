# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.backtest.backtest_regime_state_anchored
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.regime.core.anchored_state_machine; zephyr.data.implementations.internal_compute_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] regime_state_anchored 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致（本文件由生产表 create_table_query 逆向落档，2026-09-14）；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""backtest_regime_state_anchored 表 DDL-as-Code（category_id: backtest_regime_state_anchored）.

锚定风险四档历史表（P0-002 重印批/裁定#229：vol_pct 结构阈值四档，零拟合——态身份跨期恒定）。
数据源：anchored_state_machine（本地计算，读 c1_market.kline_index 000300 特征锚定）。
任务：anchored_state_build（daily_kline，依赖 kline_index_incremental）。
消费：TDM AGG 生产消费切换的前置供给；validate_p0_discrimination/compare_state_dualrun 校验脚本。

本文件为 c1_backtest 库首个 categories 登记件（2026-09-14 N-06 后解冻批补登，
登记裁定：见 data_asset_registry v1.9.3 同期 commit 与 night log）。
"""

from __future__ import annotations

# category_id: backtest_regime_state_anchored
# calc_mode: preload（回测/分析时预加载到内存）

REGIME_STATE_ANCHORED_DDL = """
CREATE TABLE IF NOT EXISTS c1_backtest.regime_state_anchored
(
    trade_date  Date                       COMMENT '交易日',
    dominant    LowCardinality(String)     COMMENT '锚定态（r1 低波震荡/r2 中波震荡/r3 牛市趋势/r4 熊市阴跌，固定阈值零拟合）',
    vol_pct     Nullable(Float64)          COMMENT '20日HV的250日滚动分位（锚定特征）',
    close       Nullable(Float64)          COMMENT '收盘价',
    ma20        Nullable(Float64)          COMMENT 'MA20',
    ma60        Nullable(Float64)          COMMENT 'MA60',
    ma120       Nullable(Float64)          COMMENT 'MA120',
    data_source LowCardinality(String) DEFAULT 'anchored_state_machine' COMMENT '数据来源',
    ingest_ts   DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree(ingest_ts)
ORDER BY trade_date
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "regime_state_anchored"
DATABASE = "c1_backtest"
CATEGORY_ID = "backtest_regime_state_anchored"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree(ingest_ts)"
PARTITION_KEY = ""
ORDER_BY = "trade_date"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(trade_date, dominant, vol_pct, close, ma20, ma60, ma120, data_source)"
