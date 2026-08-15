# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.meta_stock_basic
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] stock_basic 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL 语法错误->apply 执行时 CH 报错（fail-closed，不静默建错表）
# [TESTS] tests/zephyr/data/test_akshare_market_meta.py
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""stock_basic 表 DDL-as-Code（category_id: meta_stock_basic, calc_mode: preload）.

JOB-077 市场元数据与约束接入（DS-081，2026-08-15）：
    股票基本信息日快照（代码/名称/公司全称/所属行业/市场板块/上市日期），
    universe 构造基础。数据源为交易所官网清单（akshare stock_info_sh_name_code
    主板A股+科创板 / stock_info_sz_name_code A股列表），非东财接口，规避反爬。
    PIT 语义 strict：trade_date=快照交易日，按 (trade_date, symbol) ReplacingMergeTree
    同日重跑幂等替换。

    SCD-2 字段（沿袭 st_stock_list/index_constituent 既有模式）：
    - valid_from DEFAULT toDate(trade_date)：记录生效起始日
    - valid_to Nullable(Date)：记录生效终止日（NULL=当前有效）
    - updated_at DEFAULT now()：记录更新时间
    - ingest_ts DEFAULT now()：入库时间戳（audit 1.7 #ARCH-CH-025）
"""

from __future__ import annotations

# category_id: meta_stock_basic
# calc_mode: preload（universe 构造预加载维度表）

STOCK_BASIC_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.stock_basic
(
    trade_date   Date                   COMMENT '快照交易日',
    symbol       String                 COMMENT '证券代码(6位裸码)',
    name         String                 COMMENT '证券简称',
    fullname     String                 DEFAULT '' COMMENT '公司全称(SZ清单无此列时为空)',
    industry     LowCardinality(String) DEFAULT '' COMMENT '所属行业(SZ=交易所清单口径,SH=东财行业best-effort)',
    board        LowCardinality(String) COMMENT '市场板块(沪主板/深主板/创业板/科创板/北交所,代码前缀静态规则)',
    list_date    Nullable(Date)         COMMENT '上市日期',
    data_source  LowCardinality(String) DEFAULT 'akshare' COMMENT 'data_source',
    valid_from   Date                   DEFAULT toDate(trade_date) COMMENT 'SCD-2生效起始日',
    valid_to     Nullable(Date)         COMMENT 'SCD-2生效终止日(NULL=当前有效)',
    updated_at   DateTime64(3, 'UTC')   DEFAULT now() COMMENT '记录更新时间',
    ingest_ts    DateTime64(3, 'UTC')   DEFAULT now() COMMENT 'ingest_ts',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, symbol)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "stock_basic"
DATABASE = "c1_market"
CATEGORY_ID = "meta_stock_basic"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "trade_date, symbol"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
# valid_to 需显式传入（退市/失效=终止日，有效=NULL/省略）
INSERT_COLUMNS = "(trade_date, symbol, name, fullname, industry, board, list_date, valid_to)"
