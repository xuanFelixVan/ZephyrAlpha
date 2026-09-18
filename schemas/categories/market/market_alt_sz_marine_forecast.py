# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market.market_alt_sz_marine_forecast
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] alt_sz_marine_forecast 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""深圳海洋气象预报（深圳市气象局，深圳开放数据平台 appKey 通道）。
分海区（深圳湾/大鹏湾等）逐日天气预报：风/浪/能见度/气温/湿度/降水/气压/紫外线，
与台风路径、运价链（港口作业窗口）事件对齐。RECID 唯一幂等。
"""

from __future__ import annotations

# category_id: market_alt_sz_marine_forecast
# calc_mode: preload

MARKET_ALT_SZ_MARINE_FORECAST_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_sz_marine_forecast
(
    recid          UInt64                COMMENT '源记录号(幂等键)',
    area_name      String                COMMENT '海区名',
    ddatetime      String                COMMENT '数据时间(原文)',
    forecast_time  String                COMMENT '预报目标时刻(原文)',
    is_next_day    Int16                 COMMENT '是否次日',
    weather_status String                COMMENT '天气现象描述',
    weather_pic    String                COMMENT '天气图标',
    wind_direct    String                COMMENT '风向',
    wind_speed     Float64               COMMENT '风速',
    wind_gust      Float64               COMMENT '阵风',
    wind_gust_direct String              COMMENT '阵风风向',
    temp_max       Float64               COMMENT '最高气温',
    temp_min       Float64               COMMENT '最低气温',
    humidity       Float64               COMMENT '湿度',
    humidity_max   Float64               COMMENT '最大湿度',
    rain           Float64               COMMENT '降水',
    rain_min       Float64               COMMENT '最小降水',
    visibility     Float64               COMMENT '能见度',
    visibility_min Float64               COMMENT '最小能见度',
    wave_level     String                COMMENT '浪级',
    wave_height    Float64               COMMENT '浪高',
    liusu          Float64               COMMENT '流速',
    qiya           Float64               COMMENT '气压',
    zwx            Float64               COMMENT '紫外线指数',
    yujing         String                COMMENT '预警图',
    write_time     String                COMMENT '源写入时刻(原文)',
    ingest_ts      DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY (recid)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_sz_marine_forecast"
DATABASE = "c1_market"
CATEGORY_ID = "market_alt_sz_marine_forecast"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "tuple()"
ORDER_BY = "(recid)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(recid, area_name, ddatetime, forecast_time, is_next_day, weather_status, weather_pic, wind_direct, wind_speed, wind_gust, wind_gust_direct, temp_max, temp_min, humidity, humidity_max, rain, rain_min, visibility, visibility_min, wave_level, wave_height, liusu, qiya, zwx, yujing, write_time)"
