# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_stk_limit
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] stk_limit 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL 语法错误->apply 执行时 CH 报错（fail-closed，不静默建错表）
# [TESTS] tests/zephyr/data/test_akshare_market_meta.py
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""stk_limit 表 DDL-as-Code（category_id: market_stk_limit, calc_mode: preload）.

JOB-077 市场元数据与约束接入（DS-082，2026-08-15）：
    每日涨跌停价格（涨停价/跌停价），打板策略与回测撮合必需——涨停不可买/跌停不可卖。
    akshare 无全市场涨跌停价接口（实证 dir(akshare) 仅涨跌停池类函数，只覆盖触板个股），
    故按交易所规则由昨收价计算（行业标准做法，对标 tushare stk_limit 语义）：
    limit_up/down = round_half_up(pre_close × (1±pct), 0.01)。
    pct 口径：科创板 20%（含ST）；创业板 2020-08-24 起 20%（含ST）、此前 ST 5%/非ST 10%；
    北交所 30%；主板 ST/*ST 5%、否则 10%。新股无涨跌幅限制期 limit_*=NULL。
    PIT 语义 strict：trade_date=生效交易日，pre_close 经除权除息修正
    （close_prev × adj_factor_T/adj_factor_prev）。

    SCD-2 字段（沿袭 st_stock_list/index_constituent 既有模式）：
    - valid_from DEFAULT toDate(trade_date)：记录生效起始日
    - valid_to Nullable(Date)：记录生效终止日（NULL=当前有效）
    - updated_at DEFAULT now()：记录更新时间
    - ingest_ts DEFAULT now()：入库时间戳（audit 1.7 #ARCH-CH-025）
"""

from __future__ import annotations

# category_id: market_stk_limit
# calc_mode: preload（回测撮合约束预加载）

STK_LIMIT_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.stk_limit
(
    trade_date   Date                    COMMENT '生效交易日',
    symbol       String                  COMMENT '证券代码(6位裸码)',
    pre_close    Decimal(18, 4)          COMMENT '昨收(除权除息修正后)',
    limit_up     Nullable(Decimal(18, 4)) COMMENT '涨停价(NULL=无涨跌幅限制)',
    limit_down   Nullable(Decimal(18, 4)) COMMENT '跌停价(NULL=无涨跌幅限制)',
    limit_pct    Nullable(Decimal(6, 4)) COMMENT '涨跌停幅度小数(NULL=无限制)',
    st_flag      UInt8                   DEFAULT 0 COMMENT 'ST/*ST标记(1=ST,0=非ST/未知)',
    board        LowCardinality(String)  COMMENT '市场板块(沪主板/深主板/创业板/科创板/北交所)',
    data_source  LowCardinality(String)  DEFAULT 'rule_computed' COMMENT 'data_source',
    valid_from   Date                    DEFAULT toDate(trade_date) COMMENT 'SCD-2生效起始日',
    valid_to     Nullable(Date)          COMMENT 'SCD-2生效终止日(NULL=当前有效)',
    updated_at   DateTime64(3, 'UTC')    DEFAULT now() COMMENT '记录更新时间',
    ingest_ts    DateTime64(3, 'UTC')    DEFAULT now() COMMENT 'ingest_ts',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, symbol)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "stk_limit"
DATABASE = "c1_market"
CATEGORY_ID = "market_stk_limit"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "trade_date, symbol"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
# valid_to 需显式传入（退市/失效=终止日，有效=NULL/省略）
INSERT_COLUMNS = "(trade_date, symbol, pre_close, limit_up, limit_down, limit_pct, st_flag, board, valid_to)"
