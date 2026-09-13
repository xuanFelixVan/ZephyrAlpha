# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_alt_sz_port_monthly
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] alt_sz_port_monthly 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""深圳口岸月度流量长表（3 系列并表：海港集装箱吞吐量 TEU/口岸进出口货物量/
机场空运货物量，深圳市政府口岸办公室，深圳开放数据平台 appKey 通道）。
与 alt_shipping_index（BDI 等运价）事件对齐的贸易流量验证数据。
"""

from __future__ import annotations

# category_id: market_alt_sz_port_monthly
# calc_mode: preload

MARKET_ALT_SZ_PORT_MONTHLY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_sz_port_monthly
(
    series_code  LowCardinality(String) COMMENT '系列: port_teu/port_goods/port_air',
    month_str    String                 COMMENT '月份原文(如 2018年1月)',
    month        Date                   COMMENT '月份(派生,首日)',
    value        Float64                COMMENT '数值(TEU:万标准箱/货物:万吨)',
    release_time String                 COMMENT '发布时间原文',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(month)
ORDER BY (series_code, month)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_sz_port_monthly"
DATABASE = "c1_market"
CATEGORY_ID = "market_alt_sz_port_monthly"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(month)"
ORDER_BY = "(series_code, month)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(series_code, month_str, month, value, release_time)"
