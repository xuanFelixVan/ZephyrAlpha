# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_kline_global
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] kline_global 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [TTL] permanent
"""kline_global 表 DDL-as-Code（category_id: market_kline_global, calc_mode: lazy）。

本文件是 c1_market.kline_global 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_market_tables_ddl.py 执行。

来源（designmemos 清单 #6 / GAP-F-23，2026-08-30）：
    外盘日K线表——全球指数+商品（外盘页 12 迷你卡缺口 8 标的中 5 只价格型）：
    HSI=恒生指数(HKEX, akshare stock_hk_index_daily_sina)、
    N225=日经225(JPX, akshare index_global_hist_sina 日经225指数)、
    KOSPI=首尔综合指数(KRX, akshare index_global_hist_sina 首尔综合指数)、
    CL=NYMEX WTI原油(NYMEX, akshare futures_foreign_hist CL)、
    GC=COMEX黄金(COMEX, akshare futures_foreign_hist GC)。
    DXY/美债10Y 走 macro_data FRED 通道（FRED_DXY/FRED_DGS10_US）；
    USDCNH 免费日频源实证全失效（sina forex JSONP 404/hf null/东财不可达/FRED无CNH），
    登记跳过（tasks.yaml disabled 留痕）。

口径裁定（按 ES/NQ 先例=us_futures_intraday 专用外表，而非混入 kline_index）：
    - kline_index 实证为纯沪深 1097 只（A股专属列 advance_count/decline_count +
      sh/sz/bj/hk 前缀 MATERIALIZED 派生逻辑），混入外盘会污染 A 股口径与
      backfill/完整性门禁；故外盘日K独立成表（同 a50_futures_daily 单表多品种先例）。
    - 无 name/amount 列：源（sina hf/global）无成交额字段属有意为之；
      中文名由 FOREIGN_WATCHLIST name_zh 承载（同 a50_futures_daily 先例）。
    - open_interest=新浪 position 字段（期货品种）；指数品种恒为 0。

引擎选型说明：
    日频小表（5 品种 × ~250 行/年），ReplacingMergeTree 按 (symbol, trade_date)
    去重——增量任务重拉同窗口同键静默替换，无写前 DELETE 开销
    （同 a50_futures_daily/futures_kline_qmt 日频表选型口径）。
"""

from __future__ import annotations

# category_id: market_kline_global
# calc_mode: lazy

KLINE_GLOBAL_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.kline_global
(
    trade_date    Date           COMMENT '交易日期(标的本地市场交易日)',
    symbol        LowCardinality(String) COMMENT '品种代码(HSI=恒生/N225=日经225/KOSPI=首尔综合/CL=WTI原油/GC=COMEX黄金)',
    open          Decimal(18,4)  COMMENT '开盘价',
    high          Decimal(18,4)  COMMENT '最高价',
    low           Decimal(18,4)  COMMENT '最低价',
    close         Decimal(18,4)  COMMENT '收盘价',
    volume        UInt64         COMMENT '成交量(手/股,源早期年份可为0)',
    open_interest UInt64         COMMENT '持仓量(期货品种=新浪position字段;指数品种恒为0)',
    data_source   LowCardinality(String) COMMENT '数据来源(akshare_sina)',
    ingest_ts     DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)',
    exchange LowCardinality(String) MATERIALIZED multiIf(symbol = 'HSI', 'HKEX', symbol = 'N225', 'JPX', symbol = 'KOSPI', 'KRX', symbol = 'CL', 'NYMEX', symbol = 'GC', 'COMEX', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,品种映射)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(symbol, '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "kline_global"
DATABASE = "c1_market"
CATEGORY_ID = "market_kline_global"
CALC_MODE = "lazy"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(symbol, trade_date)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT/MATERIALIZED 列由 CH 自动填充）
# 与 akshare_provider _A50_FUTURES_COLUMNS 同构——a50_futures_daily capability
# （payload.symbols 覆盖默认品种）可直接写本表（WTI=CL/黄金=GC 日线任务即此通道）。
INSERT_COLUMNS = "(trade_date, symbol, open, high, low, close, volume, open_interest, data_source)"
