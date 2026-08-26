# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_reconciliation_differences
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.trading.recon_runner（SQLite 侧既有消费方，列契约同源）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] c1_market.reconciliation_differences 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行；append-only 仅 INSERT
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1 / verify_schema_truth.py 漂移报告
# [TTL] permanent
"""reconciliation_differences 表 DDL-as-Code（category_id: market_reconciliation_differences, calc_mode: lazy）。

本文件是 c1_market.reconciliation_differences 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_market_tables_ddl.py 执行。

来源（2026-08-26 Owner 全批 DDL 三件之一，T2_closure_review §9.1 #2 / tracker #234）：
    56 号文对账差异表（回测 vs 模拟盘三层 diff）的 ClickHouse 侧承载。
    tracker #234（2026-08-21 已闭环）已在 governance.db（SQLite）建同名表，
    消费方=zephyr.trading.recon_runner._SQL_INSERT_DIFFERENCE 十列契约：
    trade_date/recon_layer/trade_id/symbol/drift_type/system_value/broker_value/
    diff/detected_at/schema_version（id 为 SQLite AUTOINCREMENT 库内主键，
    ClickHouse 无此概念不落——ORDER BY 元组承担排序）。
    本表列名/注释与 reporting/reconciliation_schema.py DDL_RECONCILIATION_DIFFERENCES
    逐列对齐（SQLite 方言 TEXT 数值串 → ClickHouse Nullable(String) 同语义承载）。

口径备注：
    - recon_layer=trade/position/cash 三层（L1 交易级 DriftType 5 类
      price/quantity/commission/missing_in_system/missing_in_broker；L2 持仓级
      position_qty_mismatch；L3 PnL 级 pnl_gap_mismatch——后两族类型值由
      recon_runner 定义，表设计预留三层口径）。
    - system_value/broker_value/diff 为 Decimal 字符串形态（缺失侧 NULL），
      与 SQLite 侧完全一致，跨库对拍无类型换算损耗。
    - detected_at 为 UTC ISO8601 字符串（消费方写入形态），不做 DateTime 强转。
    - schema_version 对齐 SQLite 侧 DEFAULT '1.0'。

引擎选型说明：
    append-only 仅 INSERT 审计轨迹类表（54 号 §3.3 口径）；同日同键重跑
    （recon_runner 重跑同 trade_date）按 (trade_date, recon_layer, trade_id,
    symbol, drift_type, detected_at) 去重幂等——detected_at 入键保留多次
    检测轨迹（审计语义），完全同键重复写静默替换。
    SETTINGS allow_nullable_key=1：trade_id Nullable 入键所需（持仓/资金层
    trade_id=NULL 语义保留，不劣化为空串）。

TRAE-082 派生列适用性说明：
    symbol 含组合级占位值 '__PORTFOLIO__'（L3 层）且 trade_id 为主维度，
    exchange/symbol_canonical 前缀推导对占位值无意义——不挂 TRAE-082 派生列；
    惯例遵循点=data_source LowCardinality + ingest_ts DateTime64(3,'UTC')
    DEFAULT now() 审计列（audit 1.7 #ARCH-CH-025）。
"""

from __future__ import annotations

from typing import Final

# category_id: market_reconciliation_differences
# calc_mode: lazy

MARKET_RECONCILIATION_DIFFERENCES_DDL: Final = """
CREATE TABLE IF NOT EXISTS c1_market.reconciliation_differences
(
    trade_date      Date                   COMMENT '结算日',
    recon_layer     LowCardinality(String) COMMENT '对账层级(trade/position/cash 三层)',
    trade_id        Nullable(String)       COMMENT '券商结算单 trade_id(持仓/资金层为 NULL)',
    symbol          String                 COMMENT '证券代码(L3 组合级=__PORTFOLIO__ 占位)',
    drift_type      String                 COMMENT '差异类型(L1 DriftType 5 类 price/quantity/commission/missing_in_system/missing_in_broker; L2 position_qty_mismatch; L3 pnl_gap_mismatch)',
    system_value    Nullable(String)       COMMENT '系统侧值(Decimal 字符串,缺失侧为 NULL)',
    broker_value    Nullable(String)       COMMENT '券商侧值(Decimal 字符串)',
    diff            Nullable(String)       COMMENT 'system - broker(Decimal 字符串)',
    detected_at     String                 COMMENT '检测时刻(UTC ISO8601)',
    schema_version  LowCardinality(String) DEFAULT '1.0' COMMENT 'schema 版本(对齐 reconciliation_schema.SCHEMA_VERSION)',
    data_source     LowCardinality(String) DEFAULT 'recon_runner' COMMENT '写入来源',
    ingest_ts       DateTime64(3, 'UTC')   DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, recon_layer, trade_id, symbol, drift_type, detected_at)
SETTINGS allow_nullable_key = 1
"""

# 表元数据
TABLE_NAME: Final = "reconciliation_differences"
DATABASE: Final = "c1_market"
CATEGORY_ID: Final = "market_reconciliation_differences"
CALC_MODE: Final = "lazy"
ENGINE: Final = "ReplacingMergeTree"
PARTITION_KEY: Final = "toYYYYMM(trade_date)"
ORDER_BY: Final = "(trade_date, recon_layer, trade_id, symbol, drift_type, detected_at)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
# 与 recon_runner._SQL_INSERT_DIFFERENCE 十列严格同序
INSERT_COLUMNS: Final = (
    "(trade_date, recon_layer, trade_id, symbol, drift_type, "
    "system_value, broker_value, diff, detected_at, schema_version)"
)
