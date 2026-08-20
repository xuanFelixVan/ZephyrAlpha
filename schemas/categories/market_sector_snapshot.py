# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_sector_snapshot
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.sector_snapshot_collector
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] sector_snapshot 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [TTL] permanent
"""sector_snapshot 表 DDL-as-Code（category_id: market_sector_snapshot, calc_mode: streaming）。

本文件是 c1_market.sector_snapshot 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

引擎选型（裁定 #ARCH-SSOT-REFERENCE-INTEGRITY-001 Phase F 治本，2026-07-22）：
    原 sector_snapshot_collector.py 内联 DDL 使用 MergeTree（允许重复，需写前 DELETE）。
    迁移到 ReplacingMergeTree：880xxx 板块实时快照（99只推送+全量轮询30秒）高频写入，
    按 (sector_code, timestamp) 去重——直接 INSERT + 后台合并，符合 ch_writer.py §7.3
    幂等性策略首选（MergeTree 写前 DELETE 留 mutations 累积，性能差）。

    本治本同步消除 apply_market_tables_ddl.py 与 sector_snapshot_collector.py 之间的
    内联 DDL 双真源（Phase 2 目标）。
"""

from __future__ import annotations

# category_id: market_sector_snapshot
# calc_mode: streaming（实时写入，无 preload）

SECTOR_SNAPSHOT_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.sector_snapshot
(
    trade_date       Date        COMMENT '交易日',
    timestamp        DateTime64(3, 'Asia/Shanghai') COMMENT '快照时间戳',
    sector_code      String      COMMENT '板块代码 880001.SH',
    market_type      LowCardinality(String) COMMENT 'sector/mkt_index',
    now_price        Decimal(18,4) COMMENT '最新价',
    open_price       Decimal(18,4) COMMENT '开盘价',
    max_price        Decimal(18,4) COMMENT '最高价',
    min_price        Decimal(18,4) COMMENT '最低价',
    last_close       Decimal(18,4) COMMENT '昨收',
    before_5min_now  Decimal(18,4) COMMENT '5分钟前最新价',
    average_price    Decimal(18,4) COMMENT '均价',
    volume           UInt64      COMMENT '成交量(板块恒为0)',
    now_vol          UInt64      COMMENT '现量',
    amount           Decimal(18,2) COMMENT '成交额',
    up_home          UInt32      COMMENT '上涨家数',
    down_home        UInt32      COMMENT '下跌家数',
    inside           UInt32      COMMENT '内盘',
    outside          UInt32      COMMENT '外盘',
    zangsu           Decimal(10,3) COMMENT '涨速',
    data_source      LowCardinality(String) COMMENT 'tqcenter_snapshot/tqcenter_push',
    fetched_at       DateTime64(3, 'UTC') COMMENT '采集时间(UTC)',
    ingest_ts        DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (sector_code, timestamp)
"""

# 表元数据
TABLE_NAME = "sector_snapshot"
DATABASE = "c1_market"
CATEGORY_ID = "market_sector_snapshot"
CALC_MODE = "streaming"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(sector_code, timestamp)"

# 列清单（用于 INSERT 时显式指定）
INSERT_COLUMNS = (
    "(trade_date, timestamp, sector_code, market_type, "
    "now_price, open_price, max_price, min_price, last_close, before_5min_now, average_price, "
    "volume, now_vol, amount, up_home, down_home, inside, outside, zangsu, "
    "data_source, fetched_at)"
)
