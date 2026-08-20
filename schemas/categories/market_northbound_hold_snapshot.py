# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.market_northbound_hold_snapshot
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] scripts/ch/apply_market_tables_ddl; zephyr.data.implementations.northbound_hold_fetcher
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] northbound_hold_snapshot 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify 退出码1
# [TESTS] tests/zephyr/data/test_northbound_hold_fetcher.py（联调实证建表+回读）
# [A_module] module_id=MOD-L04-001-NBHS | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""northbound_hold_snapshot 表 DDL-as-Code（category_id: market_northbound_hold_snapshot, calc_mode: preload）。

本文件是 c1_market.northbound_hold_snapshot 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_market_tables_ddl.py 执行。

设计真源：设计备忘 19 号（19_northbound_hold_snapshot.md）§5.2。
季度颗粒北向资金持仓快照（港交所 2024-08-19 日频断档后的替代数据源，
tushare pro.hk_hold 季度末全量快照，仅北向 SH/SZ）。

引擎选型：ReplacingMergeTree——全量覆盖写入幂等（同 (ts_code, trade_date) 重复
插入由 CH 后台合并去重），与 fetcher「每次重拉全部已发布季度」设计配对。

列清单：
#   trade_date: Date            季度末日期
#   ts_code: String             证券代码（带交易所后缀，如 600519.SH）
#   name: String                证券名称
#   hold_share: UInt64          持股数量（股）
#   hold_ratio: Float32         持股数量占 A 股百分比
#   exchange: LowCardinality(String)  SH/SZ
#   data_source: LowCardinality(String)  DEFAULT 'tushare'
#   ingested_at: DateTime64(3, 'UTC')  DEFAULT now()  入库时间（memo §5.2 列名 ingested_at，
#       类型取家族统一精度 DateTime64(3,'UTC') 对齐既有 100+ 表 ingest 审计列惯例）
"""

from __future__ import annotations

# category_id: market_northbound_hold_snapshot
# calc_mode: preload

NORTHBOUND_HOLD_SNAPSHOT_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.northbound_hold_snapshot
(
    trade_date    Date                    COMMENT '季度末日期',
    ts_code       String                  COMMENT '证券代码（带交易所后缀）',
    name          String                  COMMENT '证券名称',
    hold_share    UInt64                  COMMENT '持股数量（股）',
    hold_ratio    Float32                 COMMENT '持股数量占 A 股百分比',
    exchange      LowCardinality(String)  COMMENT 'SH/SZ（仅北向，剔除 HK 南向）',
    data_source   LowCardinality(String)  DEFAULT 'tushare' COMMENT '数据来源',
    ingested_at   DateTime64(3, 'UTC')    DEFAULT now() COMMENT '入库时间'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (ts_code, trade_date)
"""

# 表元数据
TABLE_NAME = "northbound_hold_snapshot"
DATABASE = "c1_market"
CATEGORY_ID = "market_northbound_hold_snapshot"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "ts_code, trade_date"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
INSERT_COLUMNS = "(trade_date, ts_code, name, hold_share, hold_ratio, exchange, data_source)"
