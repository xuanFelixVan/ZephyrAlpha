# [BLUEPRINT] MOD-SIG-163 | docs/_working/infoaxis/11_equity_workbook.md §2
# [MODULE] schemas.categories.fundamental.equity_link_signal
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.signal_ashare.equity_link_signals (写，写侧唯一); L3-12-2 席位归并/X-S1 卖出委托（读，二期）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] DDL 唯一真源；一行=某业务日某信号族某主体的关联信号（ReplacingMergeTree 幂等）;
#   family 封闭三值 nium_san_cross/same_holder_link/pledge_chain; targets=管道分隔实体列;
#   PIT 锚=装配日（底座双时态由装配器保证）; DateTime64(3)+显式时区
# [MODIFY-GUARD] schema-change
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] verify_schema_truth.py 报告漂移
# [TESTS] tests/signal_ashare/test_equity_link_signals.py
# [A_module] module_id=MOD-SIG-138E | layer=schema | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] mod-sig-138e-equity-link-signal-20261014
"""equity_link_signal 表 DDL-as-Code——股权三信号族（st-infoaxis P2 股权首刀）。"""

from __future__ import annotations

TABLE_NAME = "c3_fundamental.equity_link_signal"
DATABASE = "c3_fundamental"
EQUITY_LINK_SIGNAL_DDL = """
CREATE TABLE IF NOT EXISTS c3_fundamental.equity_link_signal
(
    trade_date  Date                            COMMENT '业务日T(装配批)',
    family      LowCardinality(String)          COMMENT '信号族:nium_san_cross/same_holder_link/pledge_chain',
    subject     LowCardinality(String)          COMMENT '主体(牛散人名/持有人名/质押股东)',
    targets     String                          COMMENT '关联标的集(管道|分隔实体或代码;单标的=symbol)',
    direction   Int8                            COMMENT '方向(+1 联动受益/-1 风险压制)',
    strength    Float64                         COMMENT '强度(跨票数/质押率归一)',
    evidence    String               DEFAULT '' COMMENT '证据(edge_holding 计数/质押比等)',
    detail      String               DEFAULT '' COMMENT '明细',
    ingest_ts   DateTime64(3, 'UTC') DEFAULT now64(3) COMMENT '入库时间(DB 侧生成;RULE-SCHEMA-TZ)'
)
ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, family, subject)
COMMENT '股权三信号族(st-infoaxis P2 股权首刀:牛散跨票/同持有人联动/质押链;消费=L3-12-2 席位归并+X-S1 卖出域二期)'
"""
DDL = EQUITY_LINK_SIGNAL_DDL
INSERT_COLUMNS = (
    "trade_date",
    "family",
    "subject",
    "targets",
    "direction",
    "strength",
    "evidence",
    "detail",
)
