# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_us_futures_intraday
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] us_futures_intraday 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [TTL] permanent
"""us_futures_intraday 表 DDL-as-Code（category_id: market_us_futures_intraday, calc_mode: lazy）。

本文件是 c1_market.us_futures_intraday 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_market_tables_ddl.py 执行。

来源（92号清单 §7.2 / 44号备忘 §9.8 通道3，2026-08-21 Owner 裁定五）：
    美股期指 ES/NQ + 新交所 A50（CHA50CFD）盘中实时快照采集表。
    北京 9:30-15:00 时 CME Globex 正在交易，是亚洲时段唯一美股实时风险计。
    主源=新浪 hq.sinajs.cn hf 通道（秒级行情时间）；兜底=东财 futures_global_spot_em
    快照级（无行情时间戳，degraded=1 标记，timestamp 落采集时刻）。
    接口实证：docs/_working/reports/2026-08-22-foreign-interface-evaluation.md。

引擎选型说明：
    高频快照写入表（intraday_realtime 5 分钟轮询），ReplacingMergeTree 按
    (symbol, trade_date, timestamp) 去重——主源时间戳停滞（休市冻结态）时重跑
    同键静默替换，无写前 DELETE 开销（同 auction_book 表选型口径）。

口径备注：
    - timestamp 为主源行情时间（quote_date+quote_time 合成，Asia/Shanghai 口径）；
      兜底源无行情时间戳，timestamp=采集时刻且 degraded=1，消费端须按 degraded 过滤。
    - 涨跌幅不在采集层自算（(last_price-prev_settle)/prev_settle 由消费端派生），
      异动规则引擎属 futures_basis_monitor 施工面，本表只承载采集结果。
    - exchange/symbol_canonical 为 TRAE-082 MATERIALIZED 派生列
      （ES/NQ→CME，CHA50CFD→SGX），INSERT 不写入。
"""

from __future__ import annotations

# category_id: market_us_futures_intraday
# calc_mode: lazy

US_FUTURES_INTRADAY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.us_futures_intraday
(
    trade_date    Date           COMMENT '行情日期(主源quote_date;兜底源=采集当日)',
    timestamp     DateTime64(3, 'Asia/Shanghai') COMMENT '行情时间戳(兜底源无时间戳时=采集时刻,见degraded)',
    symbol        String         COMMENT '品种代码(ES/NQ/CHA50CFD)',
    last_price    Decimal(18,4)  COMMENT '最新价',
    bid           Decimal(18,4)  COMMENT '买价(兜底源置NULL:东财买盘为量非价)',
    ask           Decimal(18,4)  COMMENT '卖价(兜底源置NULL:同上)',
    open          Decimal(18,4)  COMMENT '开盘价',
    high          Decimal(18,4)  COMMENT '最高价',
    low           Decimal(18,4)  COMMENT '最低价',
    prev_settle   Decimal(18,4)  COMMENT '昨日结算价(涨跌幅基准,消费端自算)',
    open_interest UInt64         COMMENT '持仓量(休市/兜底源可为0)',
    name_cn       String         COMMENT '中文名(源数据)',
    data_source   LowCardinality(String) COMMENT '数据来源(sina_hf/eastmoney_em)',
    degraded      UInt8          COMMENT '降级标记(0=主源新浪hf,1=兜底东财快照无行情时间戳)',
    ingest_ts     DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)',
    exchange LowCardinality(String) MATERIALIZED multiIf(symbol IN ('ES', 'NQ'), 'CME', symbol = 'CHA50CFD', 'SGX', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,品种映射)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(symbol, '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date, timestamp)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "us_futures_intraday"
DATABASE = "c1_market"
CATEGORY_ID = "market_us_futures_intraday"
CALC_MODE = "lazy"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(symbol, trade_date, timestamp)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT/MATERIALIZED 列由 CH 自动填充）
INSERT_COLUMNS = (
    "(trade_date, timestamp, symbol, last_price, bid, ask, open, high, low, "
    "prev_settle, open_interest, name_cn, data_source, degraded)"
)
