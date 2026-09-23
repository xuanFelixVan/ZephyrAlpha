# [BLUEPRINT] MOD-SIG-026 supplement | docs/_working/sector_line/sector_layer_skeleton_v0.md §4-§5 + 考试卡 D2（docs/_working/sector_line/sector_prereg_exam_cards_v0.md）
# [MODULE] schemas.categories.sector_preference
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.data.sector_state_pipeline(写); L2 门/选股漏斗(读 banned_quadrant+tilt);
#   D2 预注册考试跑批(读)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 表 DDL 唯一真源（DDL-as-Code）；ReplacingMergeTree(ingest_ts) 版本列 latest-wins（FINAL 读确定性，防写后读竞态）；
#   tilt∈[0.8,1.2] frozen（D2 卡预承诺，改阈值=升版+重考禁原地改）；时戳纪律=T日收盘态=
#   T+1盘前输入，同一 ts 禁循环；情绪轴消费 emotion_index 的 version 留痕（契约追溯）；
#   DateTime64(3)+显式时区（RULE-SCHEMA-TZ）
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->scripts/ch/verify_schema_truth.py 报告漂移
# [TESTS] tests/signal_ashare/sector/test_sector_state_aggregator.py（映射表级）
# [TTL] permanent
"""sector_preference 表 DDL-as-Code（大盘×情绪→板块偏好映射表，st-secbuild-20260923 批2）。

本文件是 c1_market.sector_preference 表结构的唯一真源（DDL-as-Code 模式）。
设计真源：骨架稿 v0 §4-§5（水温响应面的板块层兄弟件——gate 管"放行门槛"，
preference 管"偏好倾斜"，共享两轴输入，输出不重叠）。

设计决策：
1. ReplacingMergeTree ORDER BY (trade_date, stage)——每日每 stage 单行（市场级表非板块级）。
2. emotion_version 留痕所消费 emotion_index 的 version（跨班契约追溯）。
3. banned_quadrant=该档禁入 RRG 象限（可空；多值逗号分隔留演化空间）。
4. tilt proposed 0.8~1.2 frozen——映射规则任何阈值变更=升版本+重考（D2 卡预承诺）。
"""

from __future__ import annotations

SECTOR_PREFERENCE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.sector_preference
(
    trade_date    Date                        COMMENT '交易日',
    stage         LowCardinality(String)      COMMENT 'pre_open/intraday_vN/close_final',
    ts            DateTime64(3, 'Asia/Shanghai') COMMENT '状态时戳',
    regime_dominant LowCardinality(String)    COMMENT '大盘档（r1~r12 原值透传）',
    emotion_index Nullable(Float64)           COMMENT '情绪指数快照（消费值留痕）',
    emotion_version LowCardinality(String)    COMMENT '所消费 emotion_index 的 version（契约追溯）',
    preference_label LowCardinality(String)   COMMENT '5 档偏好标签: DEFENSIVE/BALANCED/OFFENSIVE/FOLLOW/CROWDING_WARN',
    tilt          Float64                     COMMENT '权重倾斜系数（frozen 0.8~1.2）',
    banned_quadrant String                    COMMENT '禁入 RRG 象限（可空/多个逗号分隔）',
    watch_score   Nullable(Float64)           COMMENT '市场级调节分透传',
    version       LowCardinality(String)      COMMENT '语义化版本',
    ingest_ts     DateTime64(3, 'UTC') DEFAULT now64(3) COMMENT '入库时间'
)
ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, stage)
"""
