# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market.market_alt_sz_reservoir_station
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] alt_sz_reservoir_station 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] import 期无副作用无异常（纯 DDL 字符串与常量）；DDL 语法错误由 apply_market_tables_ddl.py fail-visible 捕获
# [TESTS] 解析器同域覆盖（tests/zephyr/data/test_alt_sources.py）；表结构一致性由 apply --verify 校验
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""深圳市水务局测站基本信息表（服务 1392394662，新钥匙通道）。水库测站字典（静态）。
"""

from __future__ import annotations

# category_id: alt_sz_reservoir_station
# calc_mode: preload

MARKET_ALT_SZ_RESERVOIR_STATION_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_sz_reservoir_station
(
    stcd               String                 COMMENT '测站编码(STCD,幂等键)',
    stnm               String                 COMMENT '测站名称(STNM)',
    sttp               String                 COMMENT '测站类型(STTP)',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY (stcd)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_sz_reservoir_station"
DATABASE = "c1_market"
CATEGORY_ID = "alt_sz_reservoir_station"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "***"
ORDER_BY = "stcd"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(stcd, stnm, sttp)"
