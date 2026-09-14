# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_alt_sz_air_quality_region
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] alt_sz_air_quality_region 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] import 期无副作用无异常（纯 DDL 字符串与常量）；DDL 语法错误由 apply_market_tables_ddl.py fail-visible 捕获
# [TESTS] 解析器同域覆盖（tests/zephyr/data/test_alt_sources.py）；表结构一致性由 apply --verify 校验
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""深圳分区域空气质量（服务 29200_01003608，新钥匙通道）。六区污染物浓度×日。
"""

from __future__ import annotations

# category_id: alt_sz_air_quality_region
# calc_mode: preload

MARKET_ALT_SZ_AIR_QUALITY_REGION_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_sz_air_quality_region
(
    id                 String                 COMMENT '源记录 ID(幂等键)',
    district_code      String                 COMMENT '区域代码(CDBM)',
    district_name      String                 COMMENT '区域名称(CDMC)',
    monitor_time       String                 COMMENT '监测时间(JCSJ,原文)',
    aqi                Nullable(Float64)      COMMENT 'AQI',
    pm25               Nullable(Float64)      COMMENT 'PM2.5',
    pm10               Nullable(Float64)      COMMENT 'PM10',
    so2                Nullable(Float64)      COMMENT 'SO2',
    no2                Nullable(Float64)      COMMENT 'NO2',
    co                 Nullable(Float64)      COMMENT 'CO',
    o3                 Nullable(Float64)      COMMENT 'O3',
    grade              String                 COMMENT '空气等级(KQDJ)',
    primary_pollutant  String                 COMMENT '首要污染物(SYWRW)',
    second_pollutant   String                 COMMENT '次要污染物(CBWRW)',
    update_ts          String                 COMMENT '更新时间(UPDATETIME,毫秒原文)',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(parseDateTimeBestEffortOrZero(monitor_time))
ORDER BY (id)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_sz_air_quality_region"
DATABASE = "c1_market"
CATEGORY_ID = "alt_sz_air_quality_region"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "***"
ORDER_BY = "id"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(id, district_code, district_name, monitor_time, aqi, pm25, pm10, so2, no2, co, o3, grade, primary_pollutant, second_pollutant, update_ts)"
