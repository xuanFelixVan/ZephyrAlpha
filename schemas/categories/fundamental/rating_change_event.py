# [BLUEPRINT] MOD-ALT-012 | docs/_working/infoaxis/12_research_workbook.md §2
# [MODULE] schemas.categories.fundamental.rating_change_event
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.alt_data.expectation_revision_assembler (写，写侧唯一); 板块催化定位（读，二期）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] DDL 唯一真源（DDL-as-Code）；一行=某业务日某标的评级变动事件（ReplacingMergeTree
#   同日刷新幂等）；评级打分真源=RATING_SCORE_MAP（consensus_daily_compute，册面不复制数值）；
#   direction 封闭三值 upgrade/downgrade（维持不落行）；DateTime64(3)+显式时区
# [MODIFY-GUARD] schema-change
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] verify_schema_truth.py 报告漂移（*_DDL 可发现）
# [TESTS] tests/alt_data/test_expectation_revision_assembler.py
# [A_module] module_id=MOD-ALT-012 | layer=schema | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] mod-alt-012-rating-change-event-20261014
"""rating_change_event 表 DDL-as-Code——评级变动事件流（st-infoaxis P2 研报首刀）。"""

from __future__ import annotations

TABLE_NAME = "c3_fundamental.rating_change_event"
DATABASE = "c3_fundamental"
RATING_CHANGE_EVENT_DDL = """
CREATE TABLE IF NOT EXISTS c3_fundamental.rating_change_event
(
    trade_date  Date                            COMMENT '业务日T(装配批)',
    symbol      LowCardinality(String)          COMMENT '标的代码',
    event_date  Date                            COMMENT '评级事件日(research_report.publish_date PIT 锚)',
    from_score  Int32                           COMMENT '前期评级分(RATING_SCORE_MAP 真源=consensus_daily_compute)',
    to_score    Int32                           COMMENT '本期评级分(同上)',
    direction   LowCardinality(String)          COMMENT 'upgrade|downgrade(维持不落行;文本不识别跳过留痕)',
    raw_from    LowCardinality(String)          COMMENT '前期评级原文(券商原始串,规避定义差异)',
    raw_to      LowCardinality(String)          COMMENT '本期评级原文',
    detail      String               DEFAULT '' COMMENT '明细(prev_pub=前期报告日等)',
    ingest_ts   DateTime64(3, 'UTC') DEFAULT now64(3) COMMENT '入库时间(DB 侧生成;RULE-SCHEMA-TZ)'
)
ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, symbol, event_date)
COMMENT '评级变动事件流(st-infoaxis P2 研报首刀:逐票相邻两期评级推导;rating_change 源列 0/146940 全空之闭合)'
"""
DDL = RATING_CHANGE_EVENT_DDL
INSERT_COLUMNS = (
    "trade_date",
    "symbol",
    "event_date",
    "from_score",
    "to_score",
    "direction",
    "raw_from",
    "raw_to",
    "detail",
)
