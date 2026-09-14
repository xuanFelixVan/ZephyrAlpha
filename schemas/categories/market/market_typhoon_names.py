# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market.market_typhoon_names
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] alt_typhoon_names 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""历年台风中英文对照表（深圳市气象局，静态字典，台风命名表及除名替换史）。
台风名字/年份/来源国家对齐辅助字典。KEYID 唯一幂等；静态数据仅周末全量刷新。
"""

from __future__ import annotations

# category_id: market_typhoon_names
# calc_mode: preload

MARKET_TYPHOON_NAMES_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_typhoon_names
(
    keyid         UInt64                COMMENT '源KEYID(幂等键)',
    name          String                COMMENT '英文名',
    name_chn      String                COMMENT '中文名',
    country       String                COMMENT '命名国家/地区',
    start_time    String                COMMENT '启用时间(原文)',
    end_time      String                COMMENT '停用时间(原文)',
    name_meanings String                COMMENT '名字含义',
    ingest_ts     DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY (keyid)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_typhoon_names"
DATABASE = "c1_market"
CATEGORY_ID = "market_typhoon_names"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "tuple()"
ORDER_BY = "(keyid)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(keyid, name, name_chn, country, start_time, end_time, name_meanings)"
