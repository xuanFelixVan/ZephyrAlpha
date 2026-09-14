# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_alt_sz_air_quality_daily
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] alt_sz_air_quality_daily 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] import 期无副作用无异常（纯 DDL 字符串与常量）；DDL 语法错误由 apply_market_tables_ddl.py fail-visible 捕获
# [TESTS] 解析器同域覆盖（tests/zephyr/data/test_alt_sources.py）；表结构一致性由 apply --verify 校验
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""深圳空气质量日报（深圳市生态环境局，服务 1920606096，新钥匙通道）。各监测点 AQI/首要污染物/等级，58 区×日。
"""

from __future__ import annotations

# category_id: alt_sz_air_quality_daily
# calc_mode: preload

MARKET_ALT_SZ_AIR_QUALITY_DAILY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_sz_air_quality_daily
(
    xh                 String                 COMMENT '记录序号(幂等键,UUID)',
    monitor_name       String                 COMMENT '监测点名称(JCDWMC)',
    monitor_time       String                 COMMENT '监测时间(JCSJ,原文)',
    aqi                Nullable(Int32)        COMMENT 'AQI 指数',
    level              String                 COMMENT '空气质量等级(ZSLB)',
    level_class        String                 COMMENT '等级类别(ZSJB)',
    level_color        String                 COMMENT '等级颜色(YSJB)',
    primary_pollutant  String                 COMMENT '首要污染物(SYWRW)',
    health_note        String                 COMMENT '健康状况(JKYXZK)',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(parseDateTimeBestEffortOrZero(monitor_time))
ORDER BY (xh)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_sz_air_quality_daily"
DATABASE = "c1_market"
CATEGORY_ID = "alt_sz_air_quality_daily"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "***"
ORDER_BY = "xh"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(xh, monitor_name, monitor_time, aqi, level, level_class, level_color, primary_pollutant, health_note)"
