# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.market.market_cffex_member_ranking
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] market_cffex_member_ranking 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""market_cffex_member_ranking（中金所前 20 会员持仓排名长表）DDL-as-Code
（category_id: market_cffex_member_ranking）.

altdata_line 09 清单 D6 行情补充·A8 中金所会员持仓族（2026-09-18 夜班施工，st-datapack-20260918）。
中金所每日盘后公布的会员成交/持仓排名：按品种合约分别取成交量、持买单量、持卖单量
前 20 名会员明细（成交甜会员/持买会员/持卖会员三榜同行 rank 对齐存储，源端原始结构）。

源：akshare get_cffex_rank_table(date=YYYYMMDD)（中金所官网成交持仓排名公开数据，
免费无 key）。返回 dict{合约: DataFrame}，实测（2026-09-18）：
    列=rank/vol/vol_chg/vol_party_name/long_open_interest/long_open_interest_chg/
       long_party_name/short_open_interest/short_open_interest_chg/short_party_name/
       symbol/variety；每合约 ~21 行（rank 1-20 + 合计行如实保留，rank=0 即合计）。
    源端延迟大：单日期全合约实测 ~169s（中金所站点响应慢，任务需独立超时预算）。
    历史深度：接口按日期任意查询（官网数据 2010s 起可得）——回填深度受单次 ~3min
    成本约束，本工程回填近 30 个交易日，更深历史挂账按需补（不烧源）。

与既有 futures_position 的关系（查重声明）：
    futures_position=全交易所持仓汇总口径；本表=中金所会员级前 20 排名明细，
    粒度不同（会员×合约×榜位），不构成双真源。

PIT 双轴：trade_date=交易/排名日（事实时间锚）；ingest_ts=采集时间。
单位：vol/oi=手（源端原始口径）；party_name 为会员简称（含"(代客)"等后缀如实保留）。

引擎选型：ReplacingMergeTree（同 (trade_date, symbol, rank) 幂等替换）。
PARTITION BY toYYYYMM(trade_date)。ORDER BY (trade_date, symbol, rank)。
"""

from __future__ import annotations

# category_id: market_cffex_member_ranking
# calc_mode: preload

MARKET_CFFEX_MEMBER_RANKING_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.market_cffex_member_ranking
(
    trade_date          Date                        COMMENT '交易/排名日(事实时间锚)',
    symbol              LowCardinality(String)      COMMENT '合约代码(如 IF2609)',
    variety             LowCardinality(String)      COMMENT '品种代码(如 IF)',
    rank                UInt16                      COMMENT '榜位(1-20;0=合计行,源端如实)',
    vol_party           String                      COMMENT '成交量榜会员简称',
    vol                 Nullable(Decimal(20, 2))    COMMENT '成交量(手)',
    vol_chg             Nullable(Decimal(20, 2))    COMMENT '成交量增减(手)',
    long_party          String                      COMMENT '持买单量榜会员简称',
    long_oi             Nullable(Decimal(20, 2))    COMMENT '持买单量(手)',
    long_oi_chg         Nullable(Decimal(20, 2))    COMMENT '持买单量增减(手)',
    short_party         String                      COMMENT '持卖单量榜会员简称',
    short_oi            Nullable(Decimal(20, 2))    COMMENT '持卖单量(手)',
    short_oi_chg        Nullable(Decimal(20, 2))    COMMENT '持卖单量增减(手)',
    data_source         LowCardinality(String)      DEFAULT 'akshare_cffex' COMMENT '数据来源(akshare get_cffex_rank_table=中金所官网)',
    quality_flag        UInt8                       DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts           DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳(采集时间锚)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, symbol, rank)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "market_cffex_member_ranking"
DATABASE = "c1_market"
CATEGORY_ID = "market_cffex_member_ranking"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(trade_date, symbol, rank)"

INSERT_COLUMNS = (
    "(trade_date, symbol, variety, rank, vol_party, vol, vol_chg,"
    " long_party, long_oi, long_oi_chg, short_party, short_oi, short_oi_chg,"
    " data_source, quality_flag)"
)
