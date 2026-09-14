# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.alt_sz_climate_hist
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] market_alt_sz_climate_hist 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] import 期无副作用无异常（纯 DDL 字符串与常量）；DDL 语法错误由 apply_market_tables_ddl.py fail-visible 捕获
# [TESTS] 解析器同域覆盖（tests/zephyr/data/test_alt_sources.py）；表结构一致性由 apply --verify 校验
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""气候资料_深圳国家基本气象站历史数据（服务 1287807159，主钥匙）。1953 起逐时观测。
"""

from __future__ import annotations

# category_id: market_alt_sz_climate_hist
# calc_mode: preload

MARKET_ALT_SZ_CLIMATE_HIST_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_sz_climate_hist
(
    ddatetime      String                 COMMENT '观测时刻(DDATETIME,幂等键原文)',
    ddate          Date                   COMMENT '日期(派生,分区键)',
    pressure       String                 COMMENT '气压(P,原文)',
    rain           String                 COMMENT '降水(R,原文)',
    temp           String                 COMMENT '气温(T,原文)',
    humidity       String                 COMMENT '湿度(U,原文)',
    wind_speed     String                 COMMENT '风速(V,原文)',
    wind_dir_deg   String                 COMMENT '风向角度(WDDD,原文)',
    wind_dir       String                 COMMENT '风向(WDDF,原文)',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(ddate)
ORDER BY ((ddatetime))
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_sz_climate_hist"
DATABASE = "c1_market"
CATEGORY_ID = "market_alt_sz_climate_hist"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "***"
ORDER_BY = "(ddatetime)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(ddatetime, ddate, pressure, rain, temp, humidity, wind_speed, wind_dir_deg, wind_dir)"
