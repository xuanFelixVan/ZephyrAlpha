# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_alt_sz_house_listing
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] alt_sz_house_listing 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] import 期无副作用无异常（纯 DDL 字符串与常量）；DDL 语法错误由 apply_market_tables_ddl.py fail-visible 捕获
# [TESTS] 解析器同域覆盖（tests/zephyr/data/test_alt_sources.py）；表结构一致性由 apply --verify 校验
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""二手房源信息（服务 29200_01903509，新钥匙通道）。79.4 万行挂牌房源明细。
"""

from __future__ import annotations

# category_id: alt_sz_house_listing
# calc_mode: preload

MARKET_ALT_SZ_HOUSE_LISTING_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_sz_house_listing
(
    xh                 String                 COMMENT '源序号(XH,幂等键)',
    house_name         String                 COMMENT '楼盘名(HOUSE_NAME)',
    zone               String                 COMMENT '区域(ZONE)',
    location           String                 COMMENT '地址(LU_LOCATION)',
    usage              String                 COMMENT '房屋用途(HOUSE_USAGE)',
    usage2             String                 COMMENT '用途补充(HOUSE_USAGE2)',
    built_area         Nullable(Float64)      COMMENT '建筑面积(BUILT_IN_AREA)',
    publish_date       String                 COMMENT '发布日期(PUBLISH_DATE,原文)',
    organ              String                 COMMENT '机构(ORGAN_NAME)',
    verify_code        String                 COMMENT '验证码(VERIFY_CODE)',
    full_serial        String                 COMMENT '完整序号(FULL_SERIAL_NO)',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY (xh)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_sz_house_listing"
DATABASE = "c1_market"
CATEGORY_ID = "alt_sz_house_listing"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "***"
ORDER_BY = "xh"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(xh, house_name, zone, location, usage, usage2, built_area, publish_date, organ, verify_code, full_serial)"
