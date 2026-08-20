# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_futures_term
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.c1_market_writer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] futures_term_structure 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [TTL] permanent
"""futures_term_structure 表 DDL-as-Code（category_id: market_futures_term, calc_mode: preload）。

本文件是 c1_market.futures_term_structure 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

引擎选型说明：
    蓝图 §4.0 声明"全部 ReplacingMergeTree(ingest_ts)"，§4.7 DDL 原未定义 ingest_ts
    列（蓝图内部矛盾）。Wave 2 真源回写（#ARCH-CH-025，2026-07-25）：DB 已 ALTER 加
    ingest_ts 列，本真源同步补齐，蓝图 §4.0 与 §4.7 矛盾消除。
"""

from __future__ import annotations

# category_id: market_futures_term
# calc_mode: preload（回测时预加载到内存）

FUTURES_TERM_STRUCTURE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.futures_term_structure
(
    trade_date     Date           COMMENT '交易日期',
    symbol         String         COMMENT '品种代码',
    front_contract String         COMMENT '近月合约',
    next_contract  String         COMMENT '次月合约',
    front_price    Decimal(18,4)  COMMENT '近月价格',
    next_price     Decimal(18,4)  COMMENT '次月价格',
    basis          Decimal(18,4)  COMMENT '基差(近月-次月)',
    data_source    LowCardinality(String)  COMMENT '数据来源(交易所)',
    quality_flag   UInt8          DEFAULT 1  COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts      DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)',
    exchange LowCardinality(String) DEFAULT '' COMMENT '交易所码(provider按stock_list写入TRAE-082)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "futures_term_structure"
DATABASE = "c1_market"
CATEGORY_ID = "market_futures_term"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(symbol, trade_date)"

# 列清单（用于 INSERT 时显式指定）
INSERT_COLUMNS = (
    "(trade_date, symbol, front_contract, next_contract, front_price, next_price, basis, data_source, quality_flag)"
)
