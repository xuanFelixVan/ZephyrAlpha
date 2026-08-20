# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_option_iv
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.c1_market_writer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] option_iv_surface 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [TTL] permanent
"""option_iv_surface 表 DDL-as-Code（category_id: market_option_iv, calc_mode: preload）。

本文件是 c1_market.option_iv_surface 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

引擎选型说明：
    蓝图 §4.0 声明"全部 ReplacingMergeTree(ingest_ts)"，但 §4.5 DDL 未定义 ingest_ts
    列（蓝图内部矛盾）。本文件以可执行为准——使用 ReplacingMergeTree（无版本列）。
    蓝图 §4.0 的 ingest_ts 版本列设计待 #ARCH-CH-009 后续裁定统一修正。

#ARCH-CH-021 P0-3 修复（2026-07-23）：
    ORDER BY 补 option_type。原排序键 (underlying, trade_date, strike, expiry) 缺
    option_type，导致同标的/日期/行权价/到期日的 call 与 put 在 ReplacingMergeTree
    后台合并时互相覆盖（静默丢一半数据）。补 option_type 后 call/put 不再合并。
    同时修复 miniqmt_provider 列名 opt_type→option_type（列名不匹配致值被丢弃）。
"""

from __future__ import annotations

# category_id: market_option_iv
# calc_mode: preload（回测时预加载到内存）

OPTION_IV_SURFACE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.option_iv_surface
(
    trade_date   Date           COMMENT '交易日期',
    symbol       String         COMMENT '期权代码',
    underlying   String         COMMENT '标的代码',
    strike       Decimal(18,4)  COMMENT '行权价',
    expiry       Date           COMMENT '到期日',
    iv           Decimal(18,6)  COMMENT '隐含波动率',
    option_type  LowCardinality(String)  COMMENT '期权类型(call/put)',
    delta        Decimal(18,6)  DEFAULT 0 COMMENT 'Delta',
    gamma        Decimal(18,6)  DEFAULT 0 COMMENT 'Gamma',
    theta        Decimal(18,6)  DEFAULT 0 COMMENT 'Theta',
    vega         Decimal(18,6)  DEFAULT 0 COMMENT 'Vega',
    data_source  LowCardinality(String)  COMMENT '数据来源(miniQMT/AkShare)',
    quality_flag UInt8          DEFAULT 1  COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)',
    exchange LowCardinality(String) DEFAULT '' COMMENT '交易所码(provider按stock_list写入TRAE-082)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (underlying, trade_date, strike, expiry, option_type)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "option_iv_surface"
DATABASE = "c1_market"
CATEGORY_ID = "market_option_iv"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(underlying, trade_date, strike, expiry, option_type)"

# 列清单（用于 INSERT 时显式指定）
INSERT_COLUMNS = (
    "(trade_date, symbol, underlying, strike, expiry, iv, option_type, "
    "delta, gamma, theta, vega, data_source, quality_flag)"
)
