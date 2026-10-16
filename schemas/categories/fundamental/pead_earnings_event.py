# [BLUEPRINT] MOD-SIG-164 | docs/_working/infoaxis/13_earnings_workbook.md §2
# [MODULE] schemas.categories.fundamental.pead_earnings_event
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.signal_fundamental.pead_assembly (写，写侧唯一); 九阶段选票漏斗/负面否决器（读，二期接线）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 表 DDL 唯一真源（DDL-as-Code，l9_readiness_daily 同款）；一行=某业务日某标的的
#   财报 SUE 事件（ReplacingMergeTree(ingest_ts) 同日刷新幂等）；PIT 双锚（announce_date 实锚＋
#   consensus as-of 先行情）；SUE 阈值真源=pead_event_model.SueThresholds（册面不复制数值）；
#   DateTime64(3)+显式时区 ingest_ts DB 侧生成（RULE-SCHEMA-TZ）
# [MODIFY-GUARD] schema-change
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 与 DB 不一致→scripts/ch/verify_schema_truth.py 报告漂移（*_DDL 常量可发现）
# [TESTS] tests/signal_fundamental/test_pead_assembly.py
# [A_module] module_id=MOD-SIG-110A | layer=schema | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] mod-sig-110a-pead-earnings-event-20261014
"""pead_earnings_event 表 DDL-as-Code——PEAD 装配事件表（st-infoaxis-20261013 P2 财报首刀）。

真源：docs/_working/infoaxis/13_earnings_workbook.md §2（输出契约=超预期/恶化事件流，
本表=正式财报时点 v1；预告/快报两时点表未物化留二刀——2026-10-14 实查更正）。
"""

from __future__ import annotations

TABLE_NAME = "c3_fundamental.pead_earnings_event"
DATABASE = "c3_fundamental"
PEAD_EARNINGS_EVENT_DDL = """
CREATE TABLE IF NOT EXISTS c3_fundamental.pead_earnings_event
(
    trade_date     Date                            COMMENT '业务日T(装配批;业务日真源=resolve_pf_alloc_trade_date 共用口径)',
    symbol         LowCardinality(String)          COMMENT '标的代码',
    announce_date  Date                            COMMENT '财报公告日(实际EPS PIT 实锚)',
    actual_eps     Float64                         COMMENT '实际EPS(income_statement.eps_basic)',
    consensus_eps  Float64                         COMMENT '一致预期EPS(consensus_daily as-of announce_date 最近先行情)',
    sue            Float64                         COMMENT 'SUE=(实际-预期)/|预期|(pead_event_model.compute_sue 在册口径)',
    sue_band       LowCardinality(String)          COMMENT 'SUE五档(strong_negative/negative/neutral/positive/strong_positive;阈值真源=pead_event_model.SueThresholds)',
    detail         String               DEFAULT '' COMMENT '明细/留痕(近零预期跳过原因等)',
    produced_at    DateTime64(3, 'Asia/Shanghai')  COMMENT '装配产出时刻(now_utc 真源生成)',
    ingest_ts      DateTime64(3, 'UTC') DEFAULT now64(3) COMMENT '入库时间(系统列,DB 侧生成;RULE-SCHEMA-TZ)'
)
ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, symbol, announce_date)
COMMENT 'PEAD 装配事件(st-infoaxis P2 财报首刀:正式财报时点 v1;预告/快报时点表未物化留二刀)'
"""
DDL = PEAD_EARNINGS_EVENT_DDL
INSERT_COLUMNS = (
    "trade_date",
    "symbol",
    "announce_date",
    "actual_eps",
    "consensus_eps",
    "sue",
    "sue_band",
    "detail",
    "produced_at",
)
STATUSES = ("strong_negative", "negative", "neutral", "positive", "strong_positive")
