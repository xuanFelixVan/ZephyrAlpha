# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.alt_sz_ground_obs
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] market_alt_sz_ground_obs 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] import 期无副作用无异常（纯 DDL 字符串与常量）；DDL 语法错误由 apply_market_tables_ddl.py fail-visible 捕获
# [TESTS] 解析器同域覆盖（tests/zephyr/data/test_alt_sources.py）；表结构一致性由 apply --verify 校验
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""地面观测数据_深圳国家基本气象站观测实况（服务 120238293，主钥匙）。2017 起逐时实况。
"""

from __future__ import annotations

# category_id: market_alt_sz_ground_obs
# calc_mode: preload

MARKET_ALT_SZ_GROUND_OBS_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_sz_ground_obs
(
    ddatetime      String                 COMMENT '观测时刻(DDATETIME,幂等键原文)',
    ddate          Date                   COMMENT '日期(派生,分区键)',
    pressure       Nullable(Float64)      COMMENT '气压(P,hPa)',
    rain           Nullable(Float64)      COMMENT '降水(R,mm)',
    wind_dir_deg   Nullable(Float64)      COMMENT '风向角度(FX)',
    temp           Nullable(Float64)      COMMENT '气温(T,0.1℃)',
    humidity       Nullable(Float64)      COMMENT '湿度(U,%)',
    visibility     Nullable(Float64)      COMMENT '能见度(V,米)',
    wind_speed     Nullable(Float64)      COMMENT '风速(FS,0.1m/s)',
    crt_time       String                 COMMENT '入库时刻(CRTTIME,原文)',
    crt_date       Date                   COMMENT '入库日期(派生,增量锚)',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(ddate)
ORDER BY ((ddatetime))
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_sz_ground_obs"
DATABASE = "c1_market"
CATEGORY_ID = "market_alt_sz_ground_obs"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "***"
ORDER_BY = "(ddatetime)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(ddatetime, ddate, pressure, rain, wind_dir_deg, temp, humidity, visibility, wind_speed, crt_time, crt_date)"
