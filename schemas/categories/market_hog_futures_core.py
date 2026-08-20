# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_hog_futures_core
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] hog_futures_core 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""hog_futures_core 表 DDL-as-Code（category_id: market_hog_futures_core, calc_mode: preload）.

生猪期货核心价（akshare futures_hog_core），日度更新，约1年历史。
用于期现价差分析、高频信号、与现货指数(hog_spot_index)做基差对比。

数据源：akshare futures_hog_core
    列: date/value（生猪期货核心价，元/公斤）
价格字段用 Decimal(18,4) 遵循 #ARCH-CH-026 精度裁定。
"""

from __future__ import annotations

# category_id: market_hog_futures_core
# calc_mode: preload（回测/分析时预加载到内存）

HOG_FUTURES_CORE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.hog_futures_core
(
    trade_date    Date           COMMENT '交易日期',
    value         Decimal(18,4)  COMMENT '生猪期货核心价(元/公斤)',
    ingest_ts     DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY (trade_date)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "hog_futures_core"
DATABASE = "c1_market"
CATEGORY_ID = "market_hog_futures_core"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "tuple()"
ORDER_BY = "(trade_date)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(trade_date, value)"
