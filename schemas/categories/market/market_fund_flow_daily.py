# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.market.market_fund_flow_daily
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] market_fund_flow_daily 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""market_fund_flow_daily（大盘资金流：沪深两市四档单净流入日频宽表）DDL-as-Code
（category_id: market_fund_flow_daily）.

altdata_line 09 清单 D6 行情补充·A19 东财资金流族（2026-09-18 夜班施工，st-datapack-20260918）。
全市场口径：上证+深证收盘/涨跌幅 × 主力/超大单/大单/中单/小单 净流入净额与净占比。

源：akshare stock_market_fund_flow（东方财富 datacenter 资金流向-大盘，免费无 key）。
实测（2026-09-18）：**滚动窗口约 120 个交易日**（约半年，源端固定返回最近 120 行），
逐日全量窗口重放 + ReplacingMergeTree 同键去重 = 幂等；更早历史源端不可得，
本表可回补深度以源窗口为界，日更不断供即无缺口（同 market_china_bond_yield 滚动窗口先例）。

与 c1_market.money_flow 的关系（查重声明）：
    money_flow=个股粒度资金流（tushare pro.moneyflow 主源，既有任务继续维护）；
    本表=大盘（全市场聚合）粒度，二者互补不构成双真源。
    板块粒度=既有 c1_market.sector_fund_flow（同花顺口径，sector_fund_flow_collector）。

单位口径：净额列=元（东财原始口径 float，如 -2.58e10）；占比列=%（Decimal(8,4)）。

PIT 双轴：trade_date=交易日（事实时间锚）；ingest_ts=采集时间。

引擎选型：ReplacingMergeTree（无版本列，重拉窗口幂等去重）。
PARTITION BY toYYYYMM(trade_date)。ORDER BY (trade_date)。
"""

from __future__ import annotations

# category_id: market_fund_flow_daily
# calc_mode: preload

MARKET_FUND_FLOW_DAILY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.market_fund_flow_daily
(
    trade_date      Date                        COMMENT '交易日(事实时间锚)',
    sh_close        Nullable(Decimal(12, 2))    COMMENT '上证收盘价',
    sh_pct_chg      Nullable(Decimal(8, 4))     COMMENT '上证涨跌幅(%)',
    sz_close        Nullable(Decimal(12, 2))    COMMENT '深证收盘价',
    sz_pct_chg      Nullable(Decimal(8, 4))     COMMENT '深证涨跌幅(%)',
    main_net        Nullable(Decimal(20, 2))    COMMENT '主力净流入净额(元;超大单+大单)',
    main_net_pct    Nullable(Decimal(8, 4))     COMMENT '主力净流入净占比(%)',
    super_net       Nullable(Decimal(20, 2))    COMMENT '超大单净流入净额(元)',
    super_net_pct   Nullable(Decimal(8, 4))     COMMENT '超大单净流入净占比(%)',
    big_net         Nullable(Decimal(20, 2))    COMMENT '大单净流入净额(元)',
    big_net_pct     Nullable(Decimal(8, 4))     COMMENT '大单净流入净占比(%)',
    mid_net         Nullable(Decimal(20, 2))    COMMENT '中单净流入净额(元)',
    mid_net_pct     Nullable(Decimal(8, 4))     COMMENT '中单净流入净占比(%)',
    small_net       Nullable(Decimal(20, 2))    COMMENT '小单净流入净额(元)',
    small_net_pct   Nullable(Decimal(8, 4))     COMMENT '小单净流入净占比(%)',
    data_source     LowCardinality(String)      DEFAULT 'akshare_em' COMMENT '数据来源(akshare stock_market_fund_flow=东财大盘资金流)',
    quality_flag    UInt8                       DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts       DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳(采集时间锚)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "market_fund_flow_daily"
DATABASE = "c1_market"
CATEGORY_ID = "market_fund_flow_daily"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(trade_date)"

INSERT_COLUMNS = (
    "(trade_date, sh_close, sh_pct_chg, sz_close, sz_pct_chg,"
    " main_net, main_net_pct, super_net, super_net_pct, big_net, big_net_pct,"
    " mid_net, mid_net_pct, small_net, small_net_pct, data_source, quality_flag)"
)

# 源滚动窗口（交易日）：源端固定返回最近约 120 行，窗口外历史不可回补
SOURCE_ROLLING_TRADE_DAYS = 120
