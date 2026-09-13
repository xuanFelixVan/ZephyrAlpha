# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_alt_typhoon_track
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] alt_typhoon_track 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""alt_typhoon_track 表 DDL-as-Code（category_id: market_alt_typhoon_track, calc_mode: preload）.

热带气旋路径结构化数据（深圳市气象局"热带气旋数据5.0"，深圳开放数据平台 API，
appKey 通道），另类数据气象事件层主表（2026-09-14，st-altdata-20260913）。

字段 22 项与源接口实测一致（KEYID/TCNO/经纬度/中心气压/移向移速/风速阵风/
风圈 6-7-8-10 级/级别/中英文名/发布机构/预报时效等）。时间语义：
    - ISSUEDATE = 预报发布时刻（北京时间），FORECASTDATE = 预报目标时刻
    - CRTTIME   = 平台入库时刻（北京时间）——startDate/endDate 增量即按此过滤
    - 本表按 RULE-SCHEMA-TZ 存 DateTime64(3,'UTC') 会错标时区，故原始时刻列
      保留 String 原文（零假设），另派生纯 Date 列供分区/增量锚（crt_date）
KEYID 平台全局唯一 → ReplacingMergeTree ORDER BY keyid 幂等重放。

用途：台风/极端天气事件日历，与 alt_shipping_index（运价）、hog_province_spot
（生猪区域价差）、weather_data 做事件对齐。
"""

from __future__ import annotations

# category_id: market_alt_typhoon_track
# calc_mode: preload（回测/分析时预加载到内存）

ALT_TYPHOON_TRACK_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_typhoon_track
(
    keyid          UInt64                COMMENT '平台记录序号(全局唯一)',
    tcidx          UInt32                COMMENT '台风序号(平台内部标识,一场台风一组)',
    tcno           String                COMMENT '年内编号(无名台风为0000)',
    cname          String                COMMENT '台风中文名称',
    ename          String                COMMENT '台风英文名称',
    tclevel        LowCardinality(String) COMMENT '级别:TD热带低压/TS热带风暴/STS强热带风暴/TY台风/STY强台风/SuperTY超强台风',
    issue_ts       String                COMMENT '发布时刻(北京时间原文)',
    forecast_ts    String                COMMENT '预报目标时刻(北京时间原文)',
    interval_hours UInt16                COMMENT '预报时效(小时)',
    longitude      Float64               COMMENT '预报时刻中心经度(WGS84)',
    latitude       Float64               COMMENT '预报时刻中心纬度(WGS84)',
    airpressure    Float64               COMMENT '中心气压(百帕)',
    wind           Float64               COMMENT '风速(米/秒)',
    gust           Float64               COMMENT '最大阵风(米/秒)',
    movespeed      Float64               COMMENT '移动速度(米/秒)',
    movedir        LowCardinality(String) COMMENT '移向(方位)',
    radius6        Float64               COMMENT '六级风圈半径(千米)',
    radius7        Float64               COMMENT '七级风圈半径(千米)',
    radius8        Float64               COMMENT '八级风圈半径(千米)',
    radius10       Float64               COMMENT '十级风圈半径(千米)',
    issuer         LowCardinality(String) COMMENT '发布机构代号(BABJ=北京)',
    crt_time       String                COMMENT '平台入库时刻(北京时间原文,增量锚)',
    crt_date       Date                  COMMENT '入库日期(分区/增量锚,派生自crt_time)',
    source         LowCardinality(String) COMMENT '来源接口编号',
    ingest_ts      DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(crt_date)
ORDER BY (keyid)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_typhoon_track"
DATABASE = "c1_market"
CATEGORY_ID = "market_alt_typhoon_track"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(crt_date)"
ORDER_BY = "(keyid)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = (
    "(keyid, tcidx, tcno, cname, ename, tclevel, issue_ts, forecast_ts, interval_hours, "
    "longitude, latitude, airpressure, wind, gust, movespeed, movedir, "
    "radius6, radius7, radius8, radius10, issuer, crt_time, crt_date, source)"
)
