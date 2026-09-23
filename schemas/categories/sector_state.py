# [BLUEPRINT] MOD-SIG-026 supplement | docs/_working/sector_line/sector_layer_skeleton_v0.md §5 + docs/_working/archive/2026-09/design_memos/22_sector_rotation_spec.md §3.2
# [MODULE] schemas.categories.sector_state
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.data.sector_state_pipeline(写); strategy_pipeline.daily_gate_snapshot._collect_l2
#   (L2 门三原料供料, 乙档治本); plan_engine 编排链(经 gate 快照间接读)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 表 DDL 唯一真源（DDL-as-Code）；ReplacingMergeTree(ingest_ts) 版本列 latest-wins（FINAL 读确定性，防写后读竞态）；
#   stage∈{pre_open,intraday_vN,close_final,auction}（契约四态，骨架稿§6）；时戳纪律=T日收盘态
#   (close_final)=T+1盘前输入(pre_open)，同一 ts 禁循环（板块热度禁回灌 emotion_index）；
#   DateTime64(3)+显式时区（RULE-SCHEMA-TZ）
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->scripts/ch/verify_schema_truth.py 报告漂移
# [TESTS] tests/signal_ashare/sector/test_sector_state_aggregator.py（形态级）；落库由管道验收
# [TTL] permanent
"""sector_state 表 DDL-as-Code（板块层 S10 强弱量化落库表，st-secbuild-20260923 批2）。

本文件是 c1_market.sector_state 表结构的唯一真源（DDL-as-Code 模式）。
设计真源：骨架稿 v0 §5（DDL 形态对齐 emotion_index 模式）+ 22 号 spec §3.2。

定位：每板块每日状态行（469 个 880 板 × 每交易日 2 stage）——五成分
momentum_pct/rrg_quadrant/strength/net_inflow_pct/rotation_state(市场级单值冗余 watch_score)。

设计决策：
1. ReplacingMergeTree ORDER BY (trade_date, stage, sector_code)——同键重跑幂等去重。
2. components JSON 逐成分带 status（ok/insufficient/missing，骨架稿§7 禁硬凑纪律）。
3. watch_score 冗余存便于单表回放（市场级状态注进每行，观察列不进主判）。
4. ts=状态时戳（收盘态=15:10，盘前=09:15，Asia/Shanghai 显式时区）。
"""

from __future__ import annotations

SECTOR_STATE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.sector_state
(
    trade_date    Date                        COMMENT '交易日',
    stage         LowCardinality(String)      COMMENT 'pre_open/intraday_vN/close_final',
    ts            DateTime64(3, 'Asia/Shanghai') COMMENT '状态时戳（收盘态=15:10，盘前=09:15）',
    sector_code   String                      COMMENT '板块码（880xxx 主口径）',
    sector_name   String                      COMMENT '板块名',
    momentum_pct  Nullable(Float64)           COMMENT 'q3/q5/q20 加权动量分位 [0,1]',
    rrg_quadrant  LowCardinality(String)      COMMENT 'leading/weakening/lagging/improving',
    strength      Nullable(Float64)           COMMENT '结构强度分 [0,100]',
    net_inflow_pct Nullable(Float64)          COMMENT '板块净流入截面分位 [0,1]',
    capital_score Nullable(Float64)           COMMENT '资金性质板块级得分 [-1,1]（观察列）',
    watch_score   Nullable(Float64)           COMMENT '市场级 5 状态调节分（观察列，冗余存便于单表回放）',
    components    String                      COMMENT 'JSON 明细 [{name,raw_value,percentile,weight,status}]',
    version       LowCardinality(String)      COMMENT '语义化版本，口径变更必升版',
    ingest_ts     DateTime64(3, 'UTC') DEFAULT now64(3) COMMENT '入库时间'
)
ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, stage, sector_code)
"""
