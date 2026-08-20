# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_cb_iv
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.c1_market_writer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] convertible_bond_iv 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [TTL] permanent
"""convertible_bond_iv 表 DDL-as-Code（category_id: market_cb_iv, calc_mode: preload）。

本文件是 c1_market.convertible_bond_iv 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

引擎选型说明：
    蓝图 §4.0 声明"全部 ReplacingMergeTree(ingest_ts)"，但 §4.8 DDL 未定义 ingest_ts
    列（蓝图内部矛盾）。本文件以可执行为准——使用 ReplacingMergeTree（无版本列）。
    蓝图 §4.0 的 ingest_ts 版本列设计待 #ARCH-CH-009 后续裁定统一修正。

    ingest_ts 审计列（2026-07-23 新增，audit 1.7 #ARCH-CH-025）：
    新增 ingest_ts DateTime DEFAULT now() 作为入库时间戳审计列（非版本列）。
    不入 INSERT_COLUMNS（DEFAULT 自动填充）。
"""

from __future__ import annotations

# category_id: market_cb_iv
# calc_mode: preload（回测时预加载到内存）

CONVERTIBLE_BOND_IV_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.convertible_bond_iv
(
    trade_date          Date           COMMENT '交易日期',
    symbol              String         COMMENT '转债代码',
    underlying          String         COMMENT '正股代码',
    iv                  Decimal(18,6)  COMMENT '隐含波动率',
    delta               Decimal(18,6)  DEFAULT 0 COMMENT 'Delta',
    gamma               Decimal(18,6)  DEFAULT 0 COMMENT 'Gamma',
    theta               Decimal(18,6)  DEFAULT 0 COMMENT 'Theta',
    vega                Decimal(18,6)  DEFAULT 0 COMMENT 'Vega',
    conversion_premium  Decimal(18,6)  COMMENT '转股溢价率',
    data_source         LowCardinality(String)  COMMENT '数据来源',
    quality_flag        UInt8          DEFAULT 1  COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts           DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "convertible_bond_iv"
DATABASE = "c1_market"
CATEGORY_ID = "market_cb_iv"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(symbol, trade_date)"

# 列清单（用于 INSERT 时显式指定）
INSERT_COLUMNS = (
    "(trade_date, symbol, underlying, iv, delta, gamma, theta, vega, conversion_premium, data_source, quality_flag)"
)
