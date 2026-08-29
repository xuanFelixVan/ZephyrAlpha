# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_a50_futures_daily
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] a50_futures_daily 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [TTL] permanent
"""a50_futures_daily 表 DDL-as-Code（category_id: market_a50_futures_daily, calc_mode: lazy）。

本文件是 c1_market.a50_futures_daily 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_market_tables_ddl.py 执行。

来源（A22 / 44号备忘 §9.6 通道1，M3-①d，2026-08-29）：
    富时中国A50期货（新交所 SGX，当月连续 CHA50CFD）日频历史K线表。
    用途=盘前 gap_adj 的 w3 通道（A50 夜盘涨跌幅）历史校准 + A50 交割周回溯。
    源=akshare futures_foreign_hist（新浪外盘期货历史接口，单次全量返回，
    2016-08 起约10年日K含持仓量）——源评估见
    docs/_working/reports/2026-08-29-a50-source-evaluation.md。

引擎选型说明：
    日频单品种小表（~2600 行/10年），ReplacingMergeTree 按 (symbol, trade_date)
    去重——增量任务重拉同窗口同键静默替换，无写前 DELETE 开销
    （同 futures_kline_qmt/kline_futures 日频表选型口径）。

口径备注：
    - 无成交额字段（futures_foreign_hist 不返回 amount，故本表无 amount 列，
      与 kline_futures 表不同构属有意为之）；
    - open_interest=新浪 position 字段（持仓量）；
    - exchange/symbol_canonical 为 TRAE-082 MATERIALIZED 派生列（恒为 SGX），
      INSERT 不写入。
"""

from __future__ import annotations

# category_id: market_a50_futures_daily
# calc_mode: lazy

A50_FUTURES_DAILY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.a50_futures_daily
(
    trade_date    Date           COMMENT '交易日期(新交所SGX交易日)',
    symbol        LowCardinality(String) COMMENT '品种代码(CHA50CFD=富时中国A50当月连续)',
    open          Decimal(18,4)  COMMENT '开盘价',
    high          Decimal(18,4)  COMMENT '最高价',
    low           Decimal(18,4)  COMMENT '最低价',
    close         Decimal(18,4)  COMMENT '收盘价',
    volume        UInt64         COMMENT '成交量(手,源早期年份可为0)',
    open_interest UInt64         COMMENT '持仓量(新浪position字段,源早期年份可为0)',
    data_source   LowCardinality(String) COMMENT '数据来源(akshare_sina)',
    ingest_ts     DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)',
    exchange LowCardinality(String) MATERIALIZED 'SGX' COMMENT '交易所码(TRAE-082 MATERIALIZED派生,单一品种恒为SGX)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(symbol, '.', 'SGX')) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "a50_futures_daily"
DATABASE = "c1_market"
CATEGORY_ID = "market_a50_futures_daily"
CALC_MODE = "lazy"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(symbol, trade_date)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT/MATERIALIZED 列由 CH 自动填充）
INSERT_COLUMNS = "(trade_date, symbol, open, high, low, close, volume, open_interest, data_source)"
