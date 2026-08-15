# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_suspend
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] suspend 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL 语法错误->apply 执行时 CH 报错（fail-closed，不静默建错表）
# [TESTS] tests/zephyr/data/test_akshare_market_meta.py
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""suspend 表 DDL-as-Code（category_id: market_suspend, calc_mode: preload）.

JOB-077 市场元数据与约束接入（DS-083，2026-08-15）：
    停复牌记录（停牌起止/原因），回测 MUST 排除不可成交日。
    双写入路径：
    1. 日快照（data_source=akshare_em/akshare_baidu）：东财 stock_zh_a_stop_em
       当前停牌清单为主，东财反爬封锁时降级百度 news_trade_notify_suspend_baidu
       （含停牌时间/复牌时间/停牌事项说明）。
    2. K线缺口推导（data_source=derived_kline_gap）：交易日无K线且前后均有K线
       → 停牌日，用于历史回填；区间尾部停牌无法与退市区分，不推导（已知限制）。
    PIT 语义 strict：trade_date=停牌生效交易日。

    SCD-2 字段（沿袭 st_stock_list/index_constituent 既有模式）：
    - valid_from DEFAULT toDate(trade_date)：记录生效起始日
    - valid_to Nullable(Date)：记录生效终止日（NULL=当前有效）
    - updated_at DEFAULT now()：记录更新时间
    - ingest_ts DEFAULT now()：入库时间戳（audit 1.7 #ARCH-CH-025）
"""

from __future__ import annotations

# category_id: market_suspend
# calc_mode: preload（回测撮合约束预加载）

SUSPEND_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.suspend
(
    trade_date   Date                   COMMENT '停牌生效交易日(快照日)',
    symbol       String                 COMMENT '证券代码(6位裸码)',
    name         String                 DEFAULT '' COMMENT '证券简称',
    suspend_date Nullable(Date)         COMMENT '停牌起始日',
    resume_date  Nullable(Date)         COMMENT '复牌日(NULL=未复牌)',
    reason       String                 DEFAULT '' COMMENT '停牌事项说明',
    data_source  LowCardinality(String) DEFAULT 'akshare' COMMENT 'data_source(akshare_em/akshare_baidu/derived_kline_gap)',
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
TABLE_NAME = "suspend"
DATABASE = "c1_market"
CATEGORY_ID = "market_suspend"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "trade_date, symbol"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
# valid_to 需显式传入（退市/失效=终止日，有效=NULL/省略）
INSERT_COLUMNS = "(trade_date, symbol, name, suspend_date, resume_date, reason, valid_to)"
