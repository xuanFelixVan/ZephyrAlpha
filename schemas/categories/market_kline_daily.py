# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_kline_daily
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.c1_market_writer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] kline_daily 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [TTL] permanent
"""kline_daily 表 DDL-as-Code（category_id: market_kline_daily, calc_mode: preload）。

本文件是 c1_market.kline_daily 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

命名裁定（#ARCH-SSOT-REFERENCE-INTEGRITY-001 Phase 0）：
    表名 kline_daily（以 business_data_categories.yaml 为 SSoT，非蓝图的 daily_kline）
    category_id market_kline_daily（YAML SSoT，非蓝图的 market_daily_kline）
    蓝图 §4.2 的 daily_kline / market_daily_kline 命名已过时，以 YAML 为准。

引擎选型说明：
    蓝图 §4.0 声明"全部 ReplacingMergeTree(ingest_ts)"，但 §4.2 DDL 未定义 ingest_ts
    列（蓝图内部矛盾）。本文件以可执行为准——使用 ReplacingMergeTree（无版本列），
    与 apply_market_tables_ddl.py 已部署的表结构一致。
    蓝图 §4.0 的 ingest_ts 版本列设计待 #ARCH-CH-009 后续裁定统一修正。

    ingest_ts 审计列（2026-07-23 新增，audit 1.7 #ARCH-CH-025）：
    新增 ingest_ts DateTime DEFAULT now() 作为入库时间戳审计列（非版本列）。
    新行由 CH 自动填充入库时间；旧行按 DEFAULT 惰性求值（近似值）。
    不入 INSERT_COLUMNS（DEFAULT 自动填充）。
"""

from __future__ import annotations

# category_id: market_kline_daily
# calc_mode: preload（回测时预加载到内存，性能优先）

KLINE_DAILY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.kline_daily
(
    trade_date   Date           COMMENT '交易日期',
    symbol       String         COMMENT '证券代码',
    open         Decimal(18,4)  COMMENT '开盘价',
    high         Decimal(18,4)  COMMENT '最高价',
    low          Decimal(18,4)  COMMENT '最低价',
    close        Decimal(18,4)  COMMENT '收盘价',
    volume       UInt64         COMMENT '成交量(股)',
    amount       Decimal(18,2)  COMMENT '成交额(元)',
    amplitude    Decimal(18,4)  DEFAULT 0 COMMENT '振幅(%)',
    pct_change   Decimal(18,4)  DEFAULT 0 COMMENT '涨跌幅(%)',
    change       Decimal(18,4)  DEFAULT 0 COMMENT '涨跌额(元)',
    turnover     Decimal(18,4)  DEFAULT 0 COMMENT '换手率(%)',
    adj_factor   Nullable(Decimal(18,8))  DEFAULT 1 COMMENT '复权因子(NULL=未知/缺失, 1=无复权, 0=无效已弃用→backfill为NULL. 裁定#ARCH-ADJFACTOR-NULL-001)',
    market_type  LowCardinality(String) DEFAULT 'A_share' COMMENT '资产类别(asset_class: A_share/index/sector/etf/cb/lof, INV-005 TRAE-082 1.1.0: exchange 改用独立 MATERIALIZED 列, 不复用 market_type)',
    data_source  LowCardinality(String)  COMMENT '数据来源(AkShare/miniQMT/Baostock)',
    quality_flag UInt8          DEFAULT 1  COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts    DateTime64(3, 'UTC')  DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "kline_daily"
DATABASE = "c1_market"
CATEGORY_ID = "market_kline_daily"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(symbol, trade_date)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
INSERT_COLUMNS = (
    "(trade_date, symbol, open, high, low, close, volume, amount, "
    "amplitude, pct_change, change, turnover, adj_factor, "
    "market_type, data_source, quality_flag)"
)
