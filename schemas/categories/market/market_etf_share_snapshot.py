# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.market.market_etf_share_snapshot
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] market_etf_share_snapshot 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""market_etf_share_snapshot（ETF 份额日快照：最新份额/申赎状态派生基础）DDL-as-Code
（category_id: market_etf_share_snapshot）.

altdata_line 09 清单 D6 行情补充·A11 ETF 申赎族（2026-09-18 夜班施工，st-datapack-20260918）。
全市场 ETF（沪深，实测 ~1600 只）日频份额快照：相邻两日快照差分 = 当日净申赎（份额变动），
是 ETF 申赎资金流/份额异动因子的原料层。附带 IOPV/折溢价/换手/主力净流入快照列。

源：akshare fund_etf_spot_em（东方财富 ETF 实时行情列表，免费无 key，单次全量调用）。
列含「最新份额/流通市值/总市值/数据日期/更新时间」等 37 列，本表保留申赎因子相关子集。
实测（2026-09-18）：数据日期=当日（盘后为 T 日）。

源选型说明（同族源查重）：
    fund_etf_scale_sse（上交所 ETF 规模）实测仅返回单一历史日期（2025-01-15，
    2026-09-18 实查）——源端接口退化，弃用并登记 DS-CAND rejected 留痕；
    fund_etf_fund_info_em 申购/赎回状态需逐基金循环（1600+ 次调用，QPS 不礼貌），
    本期不接（挂账：如需申赎开闭状态另行评估分批方案）；
    申赎清单（PCF 篮子）免费接口缺失，篮子级明细挂账 DS-CAND。

与既有 etf_list/etf_nav/etf_benchmark 的关系（查重声明）：
    etf_list=静态清单/etf_nav=净值/etf_benchmark=跟踪基准；
    本表=份额+申赎派生原料快照，回测口径不同（日频积累快照→差分），不构成双真源。

PIT 双轴：trade_date=数据日期（源「数据日期」列，事实时间锚）；ingest_ts=采集时间。
注意：快照为当日瞬时值，盘中采集则份额/成交类列为盘中口径——任务挂盘后 daily_capital 槽。

引擎选型：ReplacingMergeTree（同 (trade_date, symbol) 幂等替换）。
PARTITION BY toYYYYMM(trade_date)。ORDER BY (trade_date, symbol)。
"""

from __future__ import annotations

# category_id: market_etf_share_snapshot
# calc_mode: preload

MARKET_ETF_SHARE_SNAPSHOT_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.market_etf_share_snapshot
(
    trade_date      Date                        COMMENT '数据日期(源端数据日期列,事实时间锚)',
    symbol          String                      COMMENT '基金代码(6位)',
    name            String                      COMMENT '基金简称',
    spot_price      Nullable(Decimal(12, 4))    COMMENT '最新价(元)',
    iopv            Nullable(Decimal(12, 4))    COMMENT 'IOPV实时估值(元)',
    premium_disc_pct Nullable(Decimal(10, 4))   COMMENT '基金折价率(%)',
    volume          Nullable(Decimal(20, 2))    COMMENT '成交量(手)',
    amount          Nullable(Decimal(20, 2))    COMMENT '成交额(元)',
    turnover_pct    Nullable(Decimal(10, 4))    COMMENT '换手率(%)',
    main_net        Nullable(Decimal(20, 2))    COMMENT '主力净流入净额(元)',
    main_net_pct    Nullable(Decimal(10, 4))    COMMENT '主力净流入净占比(%)',
    shares          Nullable(Decimal(30, 2))    COMMENT '最新份额(份;相邻日差分=净申赎)',
    circ_mv         Nullable(Decimal(20, 2))    COMMENT '流通市值(元)',
    total_mv        Nullable(Decimal(20, 2))    COMMENT '总市值(元)',
    data_source     LowCardinality(String)      DEFAULT 'akshare_em' COMMENT '数据来源(akshare fund_etf_spot_em=东财ETF列表)',
    quality_flag    UInt8                       DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts       DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳(采集时间锚)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, symbol)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "market_etf_share_snapshot"
DATABASE = "c1_market"
CATEGORY_ID = "market_etf_share_snapshot"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(trade_date, symbol)"

INSERT_COLUMNS = (
    "(trade_date, symbol, name, spot_price, iopv, premium_disc_pct, volume, amount,"
    " turnover_pct, main_net, main_net_pct, shares, circ_mv, total_mv, data_source, quality_flag)"
)
