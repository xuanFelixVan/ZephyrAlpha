# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_typhoon_landfall_history
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] alt_typhoon_landfall_history 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""历史上登陆我国的气旋全表（深圳市气象局，静态历史档案，1949 年起）。
登陆场次/登陆省份/登陆强度——事件研究历史回补与台风路径表（alt_typhoon_track）
的名字/年份对齐锚。ID 唯一幂等；静态数据仅周末全量刷新。
"""

from __future__ import annotations

# category_id: market_typhoon_landfall_history
# calc_mode: preload

MARKET_TYPHOON_LANDFALL_HISTORY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_typhoon_landfall_history
(
    id          UInt64                COMMENT '源ID(幂等键)',
    year        UInt16                COMMENT '年份',
    tcno        Int64                 COMMENT '台风编号',
    tc_en_name  String                COMMENT '台风英文名',
    tc_cn_name  String                COMMENT '台风中文名',
    land_no     UInt16                COMMENT '登陆序号(该台风第N次登陆)',
    land_lev    LowCardinality(String) COMMENT '登陆强度(TY/STS等)',
    land_prov   String                COMMENT '登陆省份',
    cyclone_num String                COMMENT '气旋编号',
    land_sum    UInt16                COMMENT '该台风总登陆次数',
    memo        String                COMMENT '备注',
    ingest_ts   DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY (id)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_typhoon_landfall_history"
DATABASE = "c1_market"
CATEGORY_ID = "market_typhoon_landfall_history"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "tuple()"
ORDER_BY = "(id)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(id, year, tcno, tc_en_name, tc_cn_name, land_no, land_lev, land_prov, cyclone_num, land_sum, memo)"
