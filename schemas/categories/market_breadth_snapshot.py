# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_breadth_snapshot
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.miniqmt_provider; zephyr.data.intraday_sentiment_loop
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] market_breadth_snapshot 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行；一行=全市场一分钟快照（无 symbol 维度，非 securities 表）
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify; tests/zephyr/data/test_market_breadth_snapshot.py
# [TTL] permanent
"""market_breadth_snapshot 表 DDL-as-Code（category_id: market_breadth_snapshot, calc_mode: lazy）。

本文件是 c1_market.market_breadth_snapshot 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_market_tables_ddl.py 执行。

来源（92号清单 §8.2 / 44号备忘 §2 表 M1-④ 行 + §6 数据源表，2026-08-22）：
    分钟级全市场宽度快照——涨跌家数/涨跌停计数/曾涨停（含炸板）/累计成交额时序。
    44号 §6 自评"miniqmt 实时可取，未落库"，本表为 M1-① 涨跌加速度（§9.1 输入
    s_t=(adv,dec,lu,attempted)+total）与 M1-③ 相似日推演（KNN 特征曲线）的数据地基；
    采集任务=tasks.yaml market_breadth_snapshot_minute（L2 intraday_minute 族）。

TRAE-082 派生列适用性说明：
    TRAE-082（trae_082_symbol_convention.yaml）三字段模型（symbol 裸码 + exchange +
    symbol_canonical MATERIALIZED）适用对象为**含 symbol 列的 securities 表**
    （lint_symbol_convention.py 同款口径：只校验含 symbol 列的 DDL）。本表一行=
    全市场聚合快照、无 symbol 维度，exchange/symbol_canonical 语义不适用（全市场
    跨 SH/SZ/BJ 三所混合，无单一交易所码）——参照同库无 symbol 聚合表先例
    （hog_spot_index/hog_futures_core）不挂 TRAE-082 派生列；惯例遵循点=
    data_source LowCardinality + ingest_ts DateTime64(3,'UTC') DEFAULT now()
    审计列（audit 1.7 #ARCH-CH-025）+ ReplacingMergeTree + 月分区。

引擎选型说明：
    分钟级快照写入表（intraday_minute 族滚动刷新），ReplacingMergeTree 按
    (trade_date, ts) 去重——同分钟重跑/补跑同键静默替换，无写前 DELETE 开销
    （同 auction_book/us_futures_intraday 表选型口径）。

口径备注：
    - ts 为采集时刻分钟截断（Asia/Shanghai）；trade_date 为调度器交易日。
    - 涨跌停判定=最新价/日内最高 vs 板块差异化涨跌停价（昨收×(1±幅度) 四舍五入
      到分）：主板 10%（ST 5%）、创业板/科创板 20%、北交所 30%——与
      akshare_provider._limit_pct_of（stk_limit 日频表）同口径；sealed=涨停且
      卖一无量（ask1 价<=0 或量=0）；attempted=日内 high 曾触及涨停价（含炸板）。
    - 新股无涨跌幅限制期/停牌无 tick 标的按昨收缺失跳过（不计入 total_count），
      属已知近似口径，留痕待首交易日实盘标定。
    - degraded=1 表示 ST 集加载失败等降级（ST 股按主板 10% 近似，涨停计数偏紧），
      消费端须按 degraded 过滤或注解。
"""

from __future__ import annotations

from typing import Final

# category_id: market_breadth_snapshot
# calc_mode: lazy（盘中实时消费由 intraday_sentiment_loop 读取，回测按需查询）

MARKET_BREADTH_SNAPSHOT_DDL: Final = """
CREATE TABLE IF NOT EXISTS c1_market.market_breadth_snapshot
(
    trade_date   Date           COMMENT '交易日期',
    ts           DateTime64(3, 'Asia/Shanghai') COMMENT '快照时间戳(分钟截断)',
    advancing    UInt32         COMMENT '上涨家数(最新价>昨收)',
    declining    UInt32         COMMENT '下跌家数(最新价<昨收)',
    flat         UInt32         COMMENT '平盘家数(最新价=昨收)',
    limit_up     UInt32         COMMENT '涨停家数(最新价达涨停价)',
    limit_down   UInt32         COMMENT '跌停家数(最新价达跌停价)',
    sealed       UInt32         COMMENT '封住涨停家数(涨停且卖一无量)',
    attempted    UInt32         COMMENT '曾涨停家数(日内最高触及涨停价,含炸板)',
    total_count  UInt32         COMMENT '参与统计标的数(有效tick数,停牌/缺昨收跳过)',
    total_amount Decimal(18,2)  COMMENT '全市场累计成交额(元,个股tick amount求和)',
    data_source  LowCardinality(String) COMMENT '数据来源(miniqmt)',
    degraded     UInt8          DEFAULT 0 COMMENT '降级标记(0=正常,1=ST集缺失按非ST幅度近似)',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, ts)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME: Final = "market_breadth_snapshot"
DATABASE: Final = "c1_market"
CATEGORY_ID: Final = "market_breadth_snapshot"
CALC_MODE: Final = "lazy"
ENGINE: Final = "ReplacingMergeTree"
PARTITION_KEY: Final = "toYYYYMM(trade_date)"
ORDER_BY: Final = "(trade_date, ts)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
INSERT_COLUMNS: Final = (
    "(trade_date, ts, advancing, declining, flat, "
    "limit_up, limit_down, sealed, attempted, total_count, total_amount, "
    "data_source, degraded)"
)
