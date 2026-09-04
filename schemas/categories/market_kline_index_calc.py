# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_kline_index_calc
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.data.implementations.index_eqw_compute; zephyr.data.c1_market_writer
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] kline_index_calc 表 DDL 唯一真源（DDL-as-Code）；自算衍生指数专用表，与官方指数真源 kline_index 责任隔离（真源唯一/责任唯一：外部官方指数 vs 本地自算衍生指标不得混表）；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""kline_index_calc 表 DDL-as-Code（category_id: market_kline_index_calc）。

本文件是 c1_market.kline_index_calc 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致。

用途：本地自算衍生指数（Owner 2026-09-04 立项，首条 EQW_ALLA 全A等权）。
    与 c1_market.kline_index（QMT 拉取的官方指数真源）分表：
    - 责任不同：官方指数=外部真源复制；自算指数=内部衍生计算，口径可演进
    - 防污染：自算 symbol（EQW_*）永不写入官方表，反向亦然

列清单：
#   trade_date: Date
#   symbol: String（自算指数代码，EQW_ALLA=全A等权）
#   name: String
#   close: Decimal(18, 4)（链乘点位，基期 2019-01-03=1000）
#   ret: Decimal(18, 8)（当日等权平均收益率，严格复权口径）
#   n_stocks: UInt32（当日参与计算股票数）
#   advance_count: UInt32
#   decline_count: UInt32
#   data_source: String（恒 'internal'）
#   quality_flag: UInt8
#   ingest_ts: DateTime64(3, 'UTC')
"""

from __future__ import annotations

# category_id: market_kline_index_calc
# calc_mode: eager

MARKET_KLINE_INDEX_CALC_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.kline_index_calc
(
    trade_date               Date,
    symbol                   String  COMMENT '自算指数代码（EQW_ALLA=全A等权）',
    name                     String  COMMENT '指数名称',
    close                    Decimal(18, 4)  COMMENT '链乘点位（基期 2019-01-03=1000）',
    ret                      Decimal(18, 8)  DEFAULT 0  COMMENT '当日等权平均收益率（复权口径，基日=0）',
    n_stocks                 UInt32  DEFAULT 0  COMMENT '参与计算股票数',
    advance_count            UInt32  DEFAULT 0  COMMENT '上涨家数',
    decline_count            UInt32  DEFAULT 0  COMMENT '下跌家数',
    data_source              String,
    quality_flag             UInt8  DEFAULT 1,
    ingest_ts                DateTime64(3, 'UTC')  DEFAULT now(),
    exchange LowCardinality(String) MATERIALIZED 'CALC' COMMENT '自算域标记（不参与交易所身份键体系，TRAE-082 兼容占位）',
    symbol_canonical String MATERIALIZED symbol COMMENT 'canonical身份键（自算代码无交易所后缀，恒等自身）'
)
ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
"""

# 表元数据
TABLE_NAME = "kline_index_calc"
DATABASE = "c1_market"
CATEGORY_ID = "market_kline_index_calc"
CALC_MODE = "eager"
ENGINE = "ReplacingMergeTree(ingest_ts)"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(symbol, trade_date)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT/MATERIALIZED 列由 CH 自动填充）
INSERT_COLUMNS = "(trade_date, symbol, name, close, ret, n_stocks, advance_count, decline_count, data_source)"
