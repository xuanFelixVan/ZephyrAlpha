# [BLUEPRINT] MOD-L04-EMOTION-INDEX
# [MODULE] schemas.categories.market.market_emotion_index
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.internal_compute_provider (_fetch_emotion_index)
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] emotion_index 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经
#              apply_market_tables_ddl.py 执行；ReplacingMergeTree (trade_date, stage) 同键幂等=重放安全
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [ERROR_CONTRACT] DDL 与 CH 实际表结构不一致→verify_schema_truth 红牌；apply 失败 fail-visible（探针核实）
# [TESTS] 无（DDL-as-code 真源件；一致性由 verify_schema_truth.py 与 apply_market_tables_ddl.verify 兜底）
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-EMOTION-INDEX | layer=module | stability=evolving | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""emotion_index 表 DDL-as-Code（category_id: market_emotion_index）.

A股市场情绪指数落库表（骨架设计稿 v0.2，契约 v0.1；st-emomine-20260922 施工）。
行=（trade_date, stage）一键；components=JSON 数组明细（契约必带）。
version 语义化：成分集变更=升 minor，权重方案变更=升 major，禁原地改。
消费：排班/仓位节流（独立状态变量，非择时信号）；禁 fear_greed 异轴顶替。
"""

from __future__ import annotations

# category_id: market_emotion_index
# calc_mode: preload（回测/分析时预加载）

EMOTION_INDEX_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.emotion_index
(
    trade_date    Date                           COMMENT '交易日',
    stage         LowCardinality(String)         COMMENT 'close_final/pre_open（v0.2 预留 auction/intraday_vN）',
    ts            DateTime64(3, 'Asia/Shanghai') COMMENT '状态时戳（收盘态15:10/盘前09:15）',
    emotion_index Float64                        COMMENT '0-1 灰度分位（0=冰点 1=沸点）',
    components    String                         COMMENT 'JSON 数组[{name,raw_value,percentile,weight,status,obs,asof,source,note}]',
    version       LowCardinality(String)         COMMENT '语义化版本（成分集/权重变更必须升版）',
    ingest_ts     DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, stage)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "emotion_index"
DATABASE = "c1_market"
CATEGORY_ID = "market_emotion_index"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(trade_date, stage)"

# 列清单（INSERT 显式列，ingest_ts 由 CH 默认填充）
INSERT_COLUMNS = "(trade_date, stage, ts, emotion_index, components, version)"
