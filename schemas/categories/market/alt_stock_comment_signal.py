# [BLUEPRINT] MOD-ALT-013 | docs/_working/infoaxis/14_retail_ir_workbook.md §2
# [MODULE] schemas.categories.market.alt_stock_comment_signal
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.alt_data.retail_comment_signals (写，写侧唯一); 情绪线 L2-05
#   daily_condition_sensor 候选（读，二期）; 板块情绪聚合/cohort_daily_ledger retail 辅列
#   （读，C3 双轨裁定后）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] DDL 唯一真源；一行=某业务日某标的散户评论信号读数（ReplacingMergeTree
#   幂等）; attention_z=当日 attention_index 全横截面 zscore（母体 std，std<1e-9→NULL）;
#   attention_chg=对前一交易日环比差（无先值→NULL）; retail_sentiment_proxy=-composite_score
#   （千股千评散户看多度与未来收益文献为反向）；千股千评无好差评枚举为既定事实，禁凭
#   连续量伪造离散档；PIT 锚=快照 trade_date（11:00UTC 日更延迟）; DateTime64(3)+显式时区
# [MODIFY-GUARD] schema-change
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] verify_schema_truth.py 报告漂移
# [TESTS] tests/alt_data/test_retail_comment_signals.py
# [A_module] module_id=MOD-ALT-013 | layer=schema | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] mod-alt-013-alt-stock-comment-signal-20261014
"""alt_stock_comment_signal 表 DDL-as-Code——散户评论信号（st-infoaxis P2 千股千评首刀）。"""

from __future__ import annotations

TABLE_NAME = "c1_market.alt_stock_comment_signal"
DATABASE = "c1_market"
ALT_STOCK_COMMENT_SIGNAL_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_stock_comment_signal
(
    trade_date             Date                            COMMENT '快照交易日',
    symbol                 LowCardinality(String)          COMMENT '股票代码(6位,与源表同形)',
    attention_z            Nullable(Float64)               COMMENT '关注指数横截面 zscore(当日全市场;母体std<1e-9=NULL)',
    attention_chg          Nullable(Float64)               COMMENT '关注指数环比=今日-前一交易日(无先值=NULL)',
    org_participation      Nullable(Float64)               COMMENT '机构参与度(0-1 原生透传,东财独占口径)',
    composite_score        Nullable(Float64)               COMMENT '综合得分(原生透传)',
    retail_sentiment_proxy Nullable(Float64)               COMMENT '散户情绪代理=-composite_score(文献反向;composite_score NULL→NULL)',
    detail                 String               DEFAULT '' COMMENT '明细(原始attention_index/环比基线日)',
    ingest_ts              DateTime64(3, 'UTC') DEFAULT now64(3) COMMENT '入库时间(DB 侧生成;RULE-SCHEMA-TZ)'
)
ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, symbol)
COMMENT '散户评论信号(st-infoaxis P2 千股千评首刀:机构参与度+注意力横截面标准化;Q8 60天采样窗退役判据绑定)'
"""
DDL = ALT_STOCK_COMMENT_SIGNAL_DDL
INSERT_COLUMNS = (
    "trade_date",
    "symbol",
    "attention_z",
    "attention_chg",
    "org_participation",
    "composite_score",
    "retail_sentiment_proxy",
    "detail",
)
