# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_sentiment_panel
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.sentiment_panel_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] sentiment_panel 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""sentiment_panel 表 DDL-as-Code（category_id: market_sentiment_panel, calc_mode: preload）.

币圈宏观情绪面板表（CAND-CRYPTO-010 落地表）。行格式与
sentiment_panel_provider._SENTIMENT_COLUMNS 严格对齐：
(metric, trade_date, value, value_classification, source, extra)

指标词表（metric）：fear_greed_index（alternative.me 恐惧贪婪指数 0-100，已实装）；
btc_dominance / etf_flow / usdt_premium（provider 骨架能力，待源接入）。
消费：F15_FNG_INDEX 信号（<20 extreme_fear 反转窗，C4 双窗及格策略的信号源）。
"""

from __future__ import annotations

# category_id: market_sentiment_panel
# calc_mode: preload（回测/分析时预加载到内存）

SENTIMENT_PANEL_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.sentiment_panel
(
    metric               LowCardinality(String) COMMENT '指标名(fear_greed_index/btc_dominance/...)',
    trade_date           Date                   COMMENT '指标日期',
    value                Float64                COMMENT '指标值',
    value_classification LowCardinality(String) DEFAULT '' COMMENT '源方分类(Extreme Fear/...)',
    source               LowCardinality(String) DEFAULT '' COMMENT '数据源(alternative.me/...)',
    extra                String                 DEFAULT '' COMMENT '扩展字段',
    ingest_ts            DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (metric, trade_date)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "sentiment_panel"
DATABASE = "c1_market"
CATEGORY_ID = "market_sentiment_panel"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(metric, trade_date)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(metric, trade_date, value, value_classification, source, extra)"
