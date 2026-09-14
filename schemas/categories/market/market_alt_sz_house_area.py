# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market.market_alt_sz_house_area
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] alt_sz_house_area 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] import 期无副作用无异常（纯 DDL 字符串与常量）；DDL 语法错误由 apply_market_tables_ddl.py fail-visible 捕获
# [TESTS] 解析器同域覆盖（tests/zephyr/data/test_alt_sources.py）；表结构一致性由 apply --verify 校验
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""一手商品房按面积统计成交（服务 29200_01903511，新钥匙通道）。面积段×区×日。
"""

from __future__ import annotations

# category_id: alt_sz_house_area
# calc_mode: preload

MARKET_ALT_SZ_HOUSE_AREA_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_sz_house_area
(
    id                 String                 COMMENT '源记录 ID(幂等键)',
    stat_date          Date                   COMMENT '统计日期(TJ_DATE)',
    zone               String                 COMMENT '区域(ZONE)',
    area_type          String                 COMMENT '面积段(AREA_TYPE)',
    cj_num             Float64                COMMENT '成交套数(CJ_NUM)',
    cj_area            Nullable(Float64)      COMMENT '成交面积(CJ_AREA)',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(stat_date)
ORDER BY (id)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_sz_house_area"
DATABASE = "c1_market"
CATEGORY_ID = "alt_sz_house_area"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "***"
ORDER_BY = "id"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(id, stat_date, zone, area_type, cj_num, cj_area)"
