# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_hog_spot_index
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] hog_spot_index 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""hog_spot_index 表 DDL-as-Code（category_id: market_hog_spot_index, calc_mode: preload）.

生猪现货价格指数（akshare index_hog_spot_price），周度更新，2015年至今约11年历史。
用于猪周期历史定位、均线趋势分析、与养殖ETF(159865)做周期相位对比。

数据源：akshare index_hog_spot_price
    列: 日期/指数/4个月均线/6个月均线/12个月均线/预售均价/成交均价/成交均重
价格字段用 Decimal(18,4) 遵循 #ARCH-CH-026 精度裁定；均线/均重为计算值用 Float64。
"""

from __future__ import annotations

# category_id: market_hog_spot_index
# calc_mode: preload（回测/分析时预加载到内存）

HOG_SPOT_INDEX_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.hog_spot_index
(
    trade_date          Date           COMMENT '统计日期(周度)',
    index_value         Decimal(18,4)  COMMENT '生猪现货价格指数',
    ma_4m               Float64        COMMENT '4个月均线',
    ma_6m               Float64        COMMENT '6个月均线',
    ma_12m              Float64        COMMENT '12个月均线',
    presale_avg_price   Decimal(18,4)  COMMENT '预售均价(元/公斤)',
    deal_avg_price      Decimal(18,4)  COMMENT '成交均价(元/公斤)',
    deal_avg_weight     Float64        COMMENT '成交均重(公斤)',
    ingest_ts           DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY (trade_date)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "hog_spot_index"
DATABASE = "c1_market"
CATEGORY_ID = "market_hog_spot_index"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "tuple()"
ORDER_BY = "(trade_date)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(trade_date, index_value, ma_4m, ma_6m, ma_12m, presale_avg_price, deal_avg_price, deal_avg_weight)"
