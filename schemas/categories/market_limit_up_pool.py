# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_limit_up_pool
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.limit_up_pool_collector
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] limit_up_pool 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1 / verify_schema_truth.py 漂移报告
# [TTL] permanent
"""limit_up_pool 表 DDL-as-Code（category_id: market_limit_up_pool, calc_mode: lazy）。

本文件是 c1_market.limit_up_pool 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_market_tables_ddl.py 执行。

来源（2026-08-26 Owner 全批 DDL 三件之一）：
    GAP-F-13 涨停池明细采集器（zephyr.data.implementations.limit_up_pool_collector，
    MOD-DAT-limit_up_pool_ingest）docstring DDL 草稿直接转正——采集器 INSERT_COLUMNS
    19 列与本表列序一一对应（exchange/symbol_canonical 为 MATERIALIZED 派生列不入列）。
    既有 limit_up_down 表仅 7 列不存封板资金/首封/炸板等源字段，本表承接
    akshare stock_zt_pool_em 全量字段（SECTOR 会话裁定：不动既有 limit_up_down 生产表）。

引擎选型说明：
    日频全量重写场景（同日重跑/补跑），ReplacingMergeTree 按 (trade_date, symbol)
    同键静默替换幂等——同 limit_up_down 既有口径。
"""

from __future__ import annotations

from typing import Final

# category_id: market_limit_up_pool
# calc_mode: lazy

MARKET_LIMIT_UP_POOL_DDL: Final = """
CREATE TABLE IF NOT EXISTS c1_market.limit_up_pool
(
    trade_date        Date                     COMMENT '交易日期',
    symbol            String                   COMMENT '证券代码(6位裸码)',
    name              String                   COMMENT '证券名称',
    close             Nullable(Decimal(18, 4)) COMMENT '最新价(收盘)',
    pct_change        Nullable(Decimal(18, 4)) COMMENT '涨跌幅(%)',
    amount            Nullable(Decimal(18, 2)) COMMENT '成交额(元)',
    turnover_rate     Nullable(Decimal(18, 4)) COMMENT '换手率(%)',
    float_market_cap  Nullable(Decimal(20, 2)) COMMENT '流通市值(元)',
    total_market_cap  Nullable(Decimal(20, 2)) COMMENT '总市值(元)',
    seal_amount       Nullable(Decimal(20, 2)) COMMENT '封板资金(元)',
    seal_ratio        Nullable(Decimal(18, 6)) COMMENT '封单比=封板资金/流通市值(采集器派生,除零/缺失→NULL)',
    first_seal_time   Nullable(String)         COMMENT '首次封板时间 HH:MM:SS',
    last_seal_time    Nullable(String)         COMMENT '最后封板时间 HH:MM:SS',
    sealed_seconds    Nullable(Int32)          COMMENT '封住时长=末封→15:00收盘秒数(采集器派生)',
    open_board_count  Nullable(Int32)          COMMENT '炸板次数(开板次数)',
    consec_limit      Nullable(Int32)          COMMENT '连板数',
    limit_stat        String                   COMMENT '涨停统计(源原始口径,如 3/2)',
    industry          LowCardinality(String)   COMMENT '所属行业',
    data_source       LowCardinality(String)   DEFAULT 'akshare' COMMENT '数据来源',
    ingest_ts         DateTime64(3, 'UTC')     DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导,同limit_up_down)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, symbol)
"""

# 表元数据
TABLE_NAME: Final = "limit_up_pool"
DATABASE: Final = "c1_market"
CATEGORY_ID: Final = "market_limit_up_pool"
CALC_MODE: Final = "lazy"
ENGINE: Final = "ReplacingMergeTree"
PARTITION_KEY: Final = "toYYYYMM(trade_date)"
ORDER_BY: Final = "(trade_date, symbol)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT/MATERIALIZED 列由 CH 自动派生）
# 与 limit_up_pool_collector.INSERT_COLUMNS 19 列严格同序
INSERT_COLUMNS: Final = (
    "(trade_date, symbol, name, close, pct_change, amount, turnover_rate, "
    "float_market_cap, total_market_cap, seal_amount, seal_ratio, "
    "first_seal_time, last_seal_time, sealed_seconds, open_board_count, "
    "consec_limit, limit_stat, industry, data_source)"
)
