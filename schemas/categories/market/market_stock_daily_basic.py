# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market.market_stock_daily_basic
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.c1_market_writer; scripts/data/backfill_stock_daily_basic.py（AKShare 换手率回填器，留盘不入库）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] stock_daily_basic 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行；日频估值基础数据（换手率/股本/市值），筹码族指标（CYQ/SCR/CYC）前置数据批
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] 本模块为 DDL 常量无运行时异常路径；表结构漂移由 apply 探针（system.columns 核对）与 config 校验器拦截
# [TESTS] tests/config/test_config_validator.py（schema 目录加载与字段校验）
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""stock_daily_basic 表 DDL-as-Code（category_id: market_stock_daily_basic, calc_mode: lazy）。

本文件是 c1_market.stock_daily_basic 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致。

数据来源：AKShare 东财历史接口 stock_zh_a_hist 的换手率列（逐标的采集，tushare daily_basic 为备选源）。
用途：筹码族指标（CYQ 获利盘/SCR 集中度/CYC 成本均线）的换手率/股本前置数据（16 号 memo 批10 依赖）。

列清单：
#   trade_date: Date
#   symbol: String（裸 6 位码，与 stock_list/kline 对齐）
#   turnover_rate: Nullable(Float64)  换手率 %
#   float_share: Nullable(Float64)    流通股本（万股，tushare 口径预留）
#   circ_mv: Nullable(Float64)        流通市值（万元，tushare 口径预留）
#   total_mv: Nullable(Float64)       总市值（万元，tushare 口径预留）
#   data_source: LowCardinality(String)
#   ingest_ts: DateTime64(3, 'UTC')
"""

from __future__ import annotations

# category_id: market_stock_daily_basic
# calc_mode: lazy

MARKET_STOCK_DAILY_BASIC_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.stock_daily_basic
(
    trade_date               Date,
    symbol                   String,
    turnover_rate            Nullable(Float64),
    float_share              Nullable(Float64),
    circ_mv                  Nullable(Float64),
    total_mv                 Nullable(Float64),
    data_source              LowCardinality(String)  DEFAULT 'akshare',
    ingest_ts                DateTime64(3, 'UTC')  DEFAULT now()
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, symbol)
"""

# 表元数据
TABLE_NAME = "stock_daily_basic"
DATABASE = "c1_market"
CATEGORY_ID = "market_stock_daily_basic"
CALC_MODE = "lazy"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
# ORDER_BY 用元组形式——本机 CH 26.6.1 实测拒绝裸逗号多键（Code 62），元组形式可过（批9 实测）
ORDER_BY = "(trade_date, symbol)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
INSERT_COLUMNS = "(trade_date, symbol, turnover_rate, float_share, circ_mv, total_mv)"
