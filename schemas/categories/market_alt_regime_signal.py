# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_alt_regime_signal
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.alt_data.alt_regime_signals
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] alt_regime_signal 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""alt_regime_signal 表 DDL-as-Code（category_id: market_alt_regime_signal, calc_mode: preload）.

市场级另类数据 regime 信号表（C-1 消费端首批，docs/_working/alt_data_consumption_plan.md §7.3）。

信号位（signal_id 词表，新增走本文件登记）：
    F4_BDI_MOMENTUM_Z20   BDI 20 日动量 z 分数（资源/周期 regime 开关）
    F14_BTC_MOMENTUM_30D  BTCUSDT 30 日收益（全球风险偏好代理）
    F15_FNG_INDEX         恐惧贪婪指数（极值反转窗：<20 extreme_fear）
    F23_LIMITUP_EMOTION   涨停板情绪周期（连板高度/晋级率 → 阶段状态机）
    F7_TYPHOON_EVENT      台风登陆事件（事件日历，灾损/运价事件窗锚）

PIT 纪律：signal_date=t 表示仅用 ≤t 收盘数据计算；ReplacingMergeTree 按
(signal_id, signal_date) 同键替换幂等。
"""

from __future__ import annotations

# category_id: market_alt_regime_signal
# calc_mode: preload（回测/分析时预加载到内存）

ALT_REGIME_SIGNAL_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_regime_signal
(
    signal_date  Date                   COMMENT '信号日期(PIT:仅用≤当日收盘数据)',
    signal_id    LowCardinality(String) COMMENT '信号ID(F4_BDI_MOMENTUM_Z20/F14_BTC_MOMENTUM_30D/F15_FNG_INDEX/F23_LIMITUP_EMOTION/F7_TYPHOON_EVENT)',
    signal_value Float64                COMMENT '信号值(各ID口径见模块文档)',
    state        LowCardinality(String) DEFAULT '' COMMENT '状态标签(risk_on/risk_off/neutral/extreme_fear/高潮/退潮/landfall...)',
    detail       String                 DEFAULT '' COMMENT 'JSON明细(组件值/事件名/窗口)',
    source       LowCardinality(String) DEFAULT 'alt_regime_signals' COMMENT '生产方',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(signal_date)
ORDER BY (signal_id, signal_date)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_regime_signal"
DATABASE = "c1_market"
CATEGORY_ID = "market_alt_regime_signal"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(signal_date)"
ORDER_BY = "(signal_id, signal_date)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(signal_date, signal_id, signal_value, state, detail, source)"
