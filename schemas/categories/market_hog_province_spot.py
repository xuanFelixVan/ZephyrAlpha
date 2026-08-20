# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_hog_province_spot
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] hog_province_spot 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""hog_province_spot 表 DDL-as-Code（category_id: market_hog_province_spot, calc_mode: preload）.

分省生猪现价（akshare spot_hog_soozhu），日度快照，覆盖全国28省。
用于区域价差分析、主产区(东北/西南)与销区(华南)价格分化研究。

数据源：akshare spot_hog_soozhu
    列: 省份/价格/涨跌幅（当天快照，无日期列，由 payload.end 补 trade_date）
价格字段用 Decimal(18,4) 遵循 #ARCH-CH-026 精度裁定；涨跌幅用 Float64。
"""

from __future__ import annotations

# category_id: market_hog_province_spot
# calc_mode: preload（回测/分析时预加载到内存）

HOG_PROVINCE_SPOT_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.hog_province_spot
(
    trade_date    Date           COMMENT '交易日期(快照日)',
    province      String         COMMENT '省份',
    price         Decimal(18,4)  COMMENT '生猪现价(元/公斤)',
    change        Float64        COMMENT '涨跌幅(元/公斤)',
    ingest_ts     DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, province)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "hog_province_spot"
DATABASE = "c1_market"
CATEGORY_ID = "market_hog_province_spot"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(trade_date, province)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(trade_date, province, price, change)"
