# [BLUEPRINT] MOD-BT-195 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] schemas.categories.market.market_kronos_prediction_daily
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] scripts/backtest/kronos_adapter.py --score-only（唯一写入方）；读侧=B-007 消费门评审（4 周样本 IC/分位胜率）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 表 DDL 唯一真源（自包含禁跨文件 import）；PIT 三时刻组写死（asof_ts 判定时刻/input_cutoff_ts 数据截断/as_of_date 截面）；预测列组由打分器写结算列组禁回填；ReplacingMergeTree 同键重算取最新（version=asof_ts）；synthetic=1 为冒烟行
# [MODIFY-GUARD] schema-change
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 与 DB 不一致 -> scripts/ch/verify_schema_truth.py 报告漂移
# [TESTS] tests/research/backtest/test_kronos_score_only.py
# [TTL] permanent
"""kronos_prediction_daily 表 DDL-as-Code（工单 GPU-02 缺件②）。

Kronos 批量推理打分（FAC-E1E 车道 E / MOD-BT-195）的**前瞻预测落表面**：
T 日收盘后对 T+1 收盘价生成 5 分位分布（0.05/0.25/0.5/0.75/0.95）+ 点估计，
逐标的逐日一行，只落不用——消费侧（src/zephyr/signal_ashare/ml_forecast/
kronos_tsfm_predictor.py 转正）另走 B-007 人工审批门，本表存在不代表已接线。

PIT 口径（工单 §2.2 三项对齐）::

    asof_ts           = 打分器起跑时刻（UTC，DateTime64(3) 显式时区）
    input_cutoff_ts   = 该标的最后一根可用 bar 的时间戳（UTC 且 <= asof_ts）
    as_of_date        = 该 bar 的截面日期（Asia/Shanghai 日历日）
    horizon/pred_len  = 'T+1' / 1（当前唯一支持档；多 horizon 属演化位）

写入契约：INSERT_COLUMNS 是写入面唯一真源，列序与本常量逐位一致；
`realized_*` 结算列组打分器**禁写**（留 NULL），将来由结算回填腿写；
同 (as_of_date, symbol, model_size, horizon) 重算取最新（version=asof_ts）。

设计决策同 judgment_next_day_forecast（UTC 显式时区/合成行标记/COMMENT 禁 ASCII 逗号）
与 factor_feature_value（同键重算取最新/可空列禁前向填充）。
"""

from __future__ import annotations

KRONOS_PREDICTION_DAILY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.kronos_prediction_daily
(
    run_id String COMMENT '打分批次血缘标识(单次 --score-only 一值)',
    symbol String COMMENT '标的(与 market_kline_daily_hfq 口径一致)',
    asof_ts DateTime64(3, 'UTC') COMMENT '判定时刻(打分器起跑 UTC PIT 锚)',
    input_cutoff_ts DateTime64(3, 'UTC') COMMENT '数据截断时刻(最后一根可用 bar UTC 且<=asof_ts)',
    as_of_date DateTime64(3, 'Asia/Shanghai') COMMENT '截面日期(该 bar 的交易日历)',
    horizon String DEFAULT 'T+1' COMMENT '预测时段(当前唯一档 T+1)',
    pred_len UInt16 DEFAULT 1 COMMENT '预测步长(交易日数)',
    target_field String DEFAULT 'close' COMMENT '预测目标字段(当前 close 通道)',
    q005 Float64 COMMENT '分布 5% 分位(跨 sample_count 条样本路径)',
    q025 Float64 COMMENT '分布 25% 分位',
    q050 Float64 COMMENT '分布 50% 分位=点估计(与 point_estimate 同值双列便于消费)',
    q075 Float64 COMMENT '分布 75% 分位',
    q095 Float64 COMMENT '分布 95% 分位',
    point_estimate Float64 COMMENT '点估计(=q050)',
    interval_width Float64 COMMENT '区间宽度(q095-q005  sharpness 侧证)',
    context_len UInt16 COMMENT '上下文 bar 数(实际喂给模型的行数)',
    sample_count UInt16 COMMENT '样本路径条数(分位跨此维取)',
    temperature Float64 DEFAULT 1.0 COMMENT '采样温度',
    top_p Float64 DEFAULT 0.9 COMMENT 'nucleus 概率阈值',
    model_size String DEFAULT 'small' COMMENT '权重档(small|daily_ft|mini)',
    data_source String DEFAULT '' COMMENT '输入表名(kline 后复权真源解析结果)',
    inputs_ref String DEFAULT '' COMMENT '输入指纹(末 bar 日期+行数+close 值)',
    synthetic UInt8 DEFAULT 0 COMMENT '合成/冒烟行标记(1=冒烟 复核后可删带铁证)',
    realized_close Nullable(Float64) COMMENT '[结算]T+1 实现收盘(打分器禁写)',
    realized_at Nullable(DateTime64(3, 'UTC')) COMMENT '[结算]实现取值时刻(打分器禁写)',
    hit_50 Nullable(UInt8) COMMENT '[结算]realized 是否落入 q025-q075(打分器禁写)',
    hit_90 Nullable(UInt8) COMMENT '[结算]realized 是否落入 q005-q095(打分器禁写)',
    settled_at Nullable(DateTime64(3, 'UTC')) COMMENT '[结算]回填时刻(非 NULL=已结算)'
)
ENGINE = ReplacingMergeTree(asof_ts)
PARTITION BY toYYYYMM(asof_ts)
ORDER BY (as_of_date, symbol, model_size, horizon)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "kronos_prediction_daily"
DATABASE = "c1_market"
ENGINE = "ReplacingMergeTree"
CATEGORY_ID = "market_kronos_prediction_daily"
PARTITION_KEY = "toYYYYMM(asof_ts)"
ORDER_BY = "(as_of_date, symbol, model_size, horizon)"

INSERT_COLUMNS = (
    "(run_id, symbol, asof_ts, input_cutoff_ts, as_of_date, horizon, pred_len, target_field,"
    " q005, q025, q050, q075, q095, point_estimate, interval_width, context_len, sample_count,"
    " temperature, top_p, model_size, data_source, inputs_ref, synthetic)"
)
