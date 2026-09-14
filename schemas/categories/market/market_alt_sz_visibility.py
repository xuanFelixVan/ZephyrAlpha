# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market.market_alt_sz_visibility
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] alt_sz_visibility 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] import 期无副作用无异常（纯 DDL 字符串与常量）；DDL 语法错误由 apply_market_tables_ddl.py fail-visible 捕获
# [TESTS] tests/zephyr/data/test_alt_sources.py::test_visibility_row_parse（解析器同域覆盖）；表结构一致性由 apply --verify 校验
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""深圳能见度探测分钟级站点流（深圳市气象局，深圳开放数据平台 appKey 通道，
服务 1580458478）。8 观测站 × 10-15 分钟粒度：V（本站能见度）/V10M（10 分钟均值）/
MINV（最小能见度）三口径，单位约米（样本 V=67790≈67.8km）。与台风路径/海洋预报
同域事件对齐（港口作业窗口/航线能见度）。幂等键 (obtid, ddatetime)。
"""

from __future__ import annotations

# category_id: market_alt_sz_visibility
# calc_mode: preload

MARKET_ALT_SZ_VISIBILITY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_sz_visibility
(
    obtid      String               COMMENT '观测站ID(幂等键)',
    obtname    String               COMMENT '观测站名',
    ddatetime  String               COMMENT '观测时刻(原文, 分钟粒度)',
    ddate      Date                 COMMENT '观测日期(派生, 分区键)',
    v          Nullable(Float64)    COMMENT '能见度(米, 原文口径)',
    v10m       Nullable(Float64)    COMMENT '10分钟平均能见度(米)',
    minv       Nullable(Float64)    COMMENT '区间最小能见度(米)',
    minvtime   Nullable(Int16)      COMMENT '最小能见度时刻(分)',
    ingest_ts  DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(ddate)
ORDER BY (obtid, ddatetime)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_sz_visibility"
DATABASE = "c1_market"
CATEGORY_ID = "market_alt_sz_visibility"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "***"
ORDER_BY = "(obtid, ddatetime)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(obtid, obtname, ddatetime, ddate, v, v10m, minv, minvtime)"
