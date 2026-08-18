# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_ipo_calendar
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] ipo_calendar 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL 语法错误->apply 执行时 CH 报错（fail-closed，不静默建错表）
# [TESTS] tests/zephyr/data/test_akshare_ipo_calendar.py
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""ipo_calendar 表 DDL-as-Code（category_id: market_ipo_calendar, calc_mode: preload）。

tracker #114 / 37号备忘 §3.2a（2026-08-17，AI-IPO-001）：
    IPO 日历与募资规模日快照——IPO 流动性抽离前瞻预警（compute_ipo_liquidity_drain）
    的数据管道。事件型流动性抽离（如 2026-07-27 长鑫科技 688825 科创板上市募资
    579-666 亿吸金）无法被 Amihud/spread 事后检测捕获，需上市日前已知的 IPO 日历
    +募资规模做前瞻预警。
    数据源：巨潮资讯网新股列表（akshare stock_new_ipo_cninfo，匿名访问，覆盖
    沪深北全市场，含申购/上市日期、发行价、总发行数量、发行市盈率）。
    募资规模派生口径：raise_amount(亿元) = 发行价(元) × 总发行数量(万股) / 10000。
    PIT 语义 strict：trade_date=快照交易日，全量快照重拉，
    按 (trade_date, symbol) ReplacingMergeTree 同日重跑幂等替换。

    已知缺口：未定档 IPO 的 listing_date 为 NULL（官方未公告上市日），
    消费侧按 listing_date 前瞻窗口过滤天然跳过，公告后次日快照自动纳入。
"""

from __future__ import annotations

# category_id: market_ipo_calendar
# calc_mode: preload（流动性前瞻预警预加载）

IPO_CALENDAR_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.ipo_calendar
(
    trade_date     Date                    COMMENT '快照交易日',
    symbol         String                  COMMENT '证券代码(6位裸码)',
    name           String                  COMMENT '证券简称',
    list_date      Nullable(Date)          COMMENT '上市日期(NULL=未定档)',
    subscribe_date Nullable(Date)          COMMENT '申购日期(NULL=未公告)',
    issue_price    Nullable(Decimal(18, 4)) COMMENT '发行价(元, NULL=未定价)',
    total_shares   Nullable(UInt64)        COMMENT '总发行数量(股, 由万股×1e4换算)',
    raise_amount   Nullable(Decimal(18, 4)) COMMENT '募资规模(亿元=发行价×总发行数量/1e8, 未定价=NULL)',
    pe_ratio       Nullable(Decimal(18, 4)) COMMENT '发行市盈率(NULL=未披露)',
    data_source    LowCardinality(String)  DEFAULT 'akshare_cninfo' COMMENT 'data_source',
    ingest_ts      DateTime64(3, 'UTC')    DEFAULT now() COMMENT 'ingest_ts',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, symbol)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "ipo_calendar"
DATABASE = "c1_market"
CATEGORY_ID = "market_ipo_calendar"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "trade_date, symbol"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT/MATERIALIZED 列由 CH 自动填充）
INSERT_COLUMNS = (
    "(trade_date, symbol, name, list_date, subscribe_date, issue_price, "
    "total_shares, raise_amount, pe_ratio, data_source)"
)
