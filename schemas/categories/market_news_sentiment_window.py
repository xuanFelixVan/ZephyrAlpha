# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_news_sentiment_window
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.intelligence.news_sentiment_analyzer; zephyr.intelligence.nightly_sentiment_window
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] news_sentiment_window 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [TTL] permanent
"""news_sentiment_window 表 DDL-as-Code（category_id: market_news_sentiment_window, calc_mode: lazy）。

本文件是 c1_market.news_sentiment_window 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_market_tables_ddl.py 执行。

来源（92号清单 §8.4 / 44号备忘 §4 表 M3-② 行 / tracker #138，2026-08-22）：
    夜间新闻/公告情绪窗口聚合落库表——tracker #138 裁定"sentiment MVP 内存态待落库，
    建表走 data_asset_registry + CH DDL-as-Code 流程（DS-104 同族）"的闭环载体。
    26号备忘 §2.7 裁定：情绪分数作事件信号的一个维度（冲击方向+强度辅助），非独立 alpha，
    故本表只承载窗口聚合结果，不承载信号决策。

引擎选型说明：
    低频窗口写入表（夜间批每日 1 行市场级 + 标的级预留；1h 整点窗可选写入），
    ReplacingMergeTree 按 (scope, symbol, window_type, window_ts) 去重——同一窗口
    重跑同键静默替换，无写前 DELETE 开销（同 sector_snapshot 表选型口径，§7.3 幂等首选）。

口径备注：
    - 夜间窗口=前一交易日 18:00（含）→ 交易日 08:00（不含），window_ts=窗口起点；
      1h 窗口=整点对齐（与 SentimentAggregator floor("h") 口径一致）。
    - scope=market 时 symbol 为空串；scope=symbol 为 #139 标的关联层预留（MVP 只写 market 级）。
    - positive/negative/neutral_count 以 polarity 符号划分（>0/<0/=0），total_count 按
      news_id 去重后计数（news_data 为 SCD 多版本表，防修正稿膨胀）。
    - top_events_json 为按 |polarity| 降序 TopN 的事件摘要 JSON 串（news_id/title/polarity/symbols），
      写入侧序列化，消费侧 json.loads。
    - window_date/exchange/symbol_canonical 为 TRAE-082 MATERIALIZED 派生列，INSERT 不写入。
"""

from __future__ import annotations

# category_id: market_news_sentiment_window
# calc_mode: lazy

NEWS_SENTIMENT_WINDOW_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.news_sentiment_window
(
    window_ts       DateTime64(3, 'Asia/Shanghai') COMMENT '窗口起点(夜间窗=前一交易日18:00整点;1h窗=整点对齐)',
    window_end      DateTime64(3, 'Asia/Shanghai') COMMENT '窗口终点(夜间窗=交易日08:00,左闭右开)',
    window_type     LowCardinality(String) DEFAULT 'night' COMMENT '窗口类型(night=夜间18:00-次日08:00/1h=整点小时窗)',
    scope           LowCardinality(String) DEFAULT 'market' COMMENT '聚合范围(market=市场级/symbol=标的级预留)',
    symbol          String         DEFAULT '' COMMENT '标的代码(scope=symbol时填,market级空串)',
    sentiment_index Float64        COMMENT '综合情绪指数[-1,1](窗口加权平均极性)',
    avg_polarity    Float64        COMMENT '窗口平均极性[-1,1]',
    positive_count  UInt32         COMMENT '正向新闻条数(polarity>0)',
    negative_count  UInt32         COMMENT '负向新闻条数(polarity<0)',
    neutral_count   UInt32         COMMENT '中性新闻条数(polarity=0)',
    total_count     UInt32         COMMENT '窗口新闻总条数(news_id去重后,防SCD修正稿膨胀)',
    top_events_json String         DEFAULT '' COMMENT '头部事件JSON(按|polarity|降序TopN:news_id/title/polarity/symbols)',
    data_source     LowCardinality(String) DEFAULT 'rule' COMMENT '打分方法(rule/llm/llm_fallback)',
    ingest_ts       DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)',
    window_date Date MATERIALIZED toDate(window_ts) COMMENT '窗口归属日(TRAE-082 MATERIALIZED派生,按日查询辅助)',
    exchange LowCardinality(String) MATERIALIZED multiIf(symbol = '', '', position(symbol, '.') > 0, splitByChar('.', symbol)[2], substring(symbol, 1, 3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(symbol, 1, 3) IN ('123', '128'), 'SZ', substring(symbol, 1, 2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(symbol, 1, 1) IN ('4', '8'), 'BJ', substring(symbol, 1, 1) IN ('5', '6', '9'), 'SH', substring(symbol, 1, 1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导;market级空串)',
    symbol_canonical String MATERIALIZED if(symbol = '' OR position(symbol, '.') > 0, symbol, concat(symbol, '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用;market级空串)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(window_ts)
ORDER BY (scope, symbol, window_type, window_ts)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "news_sentiment_window"
DATABASE = "c1_market"
CATEGORY_ID = "market_news_sentiment_window"
CALC_MODE = "lazy"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(window_ts)"
ORDER_BY = "(scope, symbol, window_type, window_ts)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT/MATERIALIZED 列由 CH 自动填充）
INSERT_COLUMNS = (
    "(window_ts, window_end, window_type, scope, symbol, sentiment_index, avg_polarity, "
    "positive_count, negative_count, neutral_count, total_count, top_events_json, data_source)"
)
