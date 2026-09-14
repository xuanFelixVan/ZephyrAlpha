# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.alt_sz_reservoir_level
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] market_alt_sz_reservoir_level 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] import 期无副作用无异常（纯 DDL 字符串与常量）；DDL 语法错误由 apply_market_tables_ddl.py fail-visible 捕获
# [TESTS] 解析器同域覆盖（tests/zephyr/data/test_alt_sources.py）；表结构一致性由 apply --verify 校验
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""深圳市水务局水库水位表（服务 1952552493，主钥匙）。7630 万行分钟级水位序列，无过滤参数（增量=ID 二分同能见度）。大表纪律：首刷限近窗，全史报批。
"""

from __future__ import annotations

# category_id: market_alt_sz_reservoir_level
# calc_mode: preload

MARKET_ALT_SZ_RESERVOIR_LEVEL_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_sz_reservoir_level
(
    id             String                 COMMENT '源记录 ID(幂等键)',
    stcd           String                 COMMENT '测站编码(STCD)',
    tm             String                 COMMENT '时间(TM,原文分钟级)',
    tdate          Date                   COMMENT '日期(派生,分区键)',
    rz             Nullable(Float64)      COMMENT '水位(RZ,米)',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(tdate)
ORDER BY ((stcd, id))
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_sz_reservoir_level"
DATABASE = "c1_market"
CATEGORY_ID = "market_alt_sz_reservoir_level"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "***"
ORDER_BY = "(stcd, id)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(id, stcd, tm, tdate, rz)"
