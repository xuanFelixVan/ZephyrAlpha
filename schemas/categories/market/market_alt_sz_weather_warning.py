# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market.market_alt_sz_weather_warning
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] alt_sz_weather_warning 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""深圳灾害性天气预警信号流（深圳市气象局，深圳开放数据平台 appKey 通道，
全平台调用量第一接口）。台风/暴雨/大风等预警的发布与解除记录——气象事件日历主干，
增量按 crt_date（入库日期）。RECID 唯一幂等。
"""

from __future__ import annotations

# category_id: market_alt_sz_weather_warning
# calc_mode: preload

MARKET_ALT_SZ_WEATHER_WARNING_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_sz_weather_warning
(
    recid          UInt64                COMMENT '源记录号(幂等键)',
    keyid          Int64                 COMMENT '源KEYID',
    tnumber        Int64                 COMMENT '预警编号',
    signal_type    String                COMMENT '预警类型(台风/暴雨/大风等)',
    signal_level   String                COMMENT '预警级别(蓝/黄/橙/红)',
    issue_state    String                COMMENT '状态(发布/解除)',
    district       String                COMMENT '预警区域',
    issue_content  String                COMMENT '预警全文',
    issue_ts       String                COMMENT '发布时刻(北京时间原文)',
    crt_time       String                COMMENT '入库时刻(北京时间原文,增量锚)',
    crt_date       Date                  COMMENT '入库日期(派生,分区锚)',
    underwriter    String                COMMENT '签发人',
    autosent_flag  Int16                 COMMENT '自动发送标记',
    autosent_count Int16                 COMMENT '自动发送数',
    trace_flag     Int16                 COMMENT '跟踪标记',
    trace_count    Int16                 COMMENT '跟踪数',
    sync_rownum    String                COMMENT '源同步行号',
    ingest_ts      DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(crt_date)
ORDER BY (recid)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_sz_weather_warning"
DATABASE = "c1_market"
CATEGORY_ID = "market_alt_sz_weather_warning"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(crt_date)"
ORDER_BY = "(recid)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(recid, keyid, tnumber, signal_type, signal_level, issue_state, district, issue_content, issue_ts, crt_time, crt_date, underwriter, autosent_flag, autosent_count, trace_flag, trace_count, sync_rownum)"
