# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.alt_sz_env_meteor
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] market_alt_sz_env_meteor 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] import 期无副作用无异常（纯 DDL 字符串与常量）；DDL 语法错误由 apply_market_tables_ddl.py fail-visible 捕获
# [TESTS] 解析器同域覆盖（tests/zephyr/data/test_alt_sources.py）；表结构一致性由 apply --verify 校验
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""预报预警数据_环境气象预报（服务 675294854，主钥匙）。环境气象等级/污染扩散条件评价。
"""

from __future__ import annotations

# category_id: market_alt_sz_env_meteor
# calc_mode: preload

MARKET_ALT_SZ_ENV_METEOR_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_sz_env_meteor
(
    id             String                 COMMENT '源记录 ID(幂等键)',
    datetime       String                 COMMENT '发布时间(DATETIME,原文)',
    area           String                 COMMENT '区域(AREA)',
    type           String                 COMMENT '类型(TYPE)',
    wr_level       String                 COMMENT '气象等级(WRLEVEL)',
    wr_index       String                 COMMENT '气象指数(WRINDEX)',
    evaluate       String                 COMMENT '评价(EVALUATE)',
    c_level        String                 COMMENT '污染扩散条件(CLEVEL)',
    continue_time  String                 COMMENT '持续时间(CONTINUETIME)',
    kq_rank        String                 COMMENT '空气等级(KQRANK)',
    zyfomite       String                 COMMENT '主要污染物(ZYFOMITE)',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY ((id))
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_sz_env_meteor"
DATABASE = "c1_market"
CATEGORY_ID = "market_alt_sz_env_meteor"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "***"
ORDER_BY = "(id)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(id, datetime, area, type, wr_level, wr_index, evaluate, c_level, continue_time, kq_rank, zyfomite)"
