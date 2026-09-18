# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.market.market_ndrc_fuel_price
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] ndrc_fuel_price 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ndrc_fuel_price（发改委成品油调价）DDL-as-Code（category_id: market_ndrc_fuel_price）.

E8 成品油（骨架 01 号文档 E 族/altdata_line 09 清单 D4 波2，2026-09-18 夜班施工）。
国家发改委汽柴油最高零售价历次调价的结构化数据集：调价窗口日 + 汽柴油价格（元/吨）+
调价幅度（元/吨）。P2 解锁件（两包交界面）：产业链分包 06 传导链引擎 N1a 成品油节点挂价消费。

源：AKShare energy_oil_hist（发改委公开调价历史，2000-06-06 起，~330 行/低频事件表）。

PIT 双轴（生效日 vs 公告日双列）：
    announce_date  = 源端"调整日期"（调价窗口日，发改委当日发布）
    effective_date = announce_date + 1 天（调价自公告日 24 时起执行，即次日历日零点生效）
    两列均入库：消费方按公告反应研究用 announce_date，按实际价格路径对齐用 effective_date。

引擎选型：
    ReplacingMergeTree（无版本列）——调价历史是终局事实（历史调价不被改写），
    同键 (announce_date) 重拉幂等替换。
    PARTITION BY toYYYYMM(announce_date)。
    ORDER BY (announce_date)。
"""

from __future__ import annotations

# category_id: market_ndrc_fuel_price
# calc_mode: preload

NDRC_FUEL_PRICE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.ndrc_fuel_price
(
    announce_date   Date                     COMMENT '公告日(=源端调整日期/调价窗口日,发改委当日发布)',
    effective_date  Date                     COMMENT '生效日(公告日24时起执行=次日历日,消费方按价格路径对齐用)',
    gasoline_price  Decimal(12, 2)           COMMENT '汽油最高零售价(元/吨,调后价)',
    diesel_price    Decimal(12, 2)           COMMENT '柴油最高零售价(元/吨,调后价)',
    gasoline_change Nullable(Decimal(12, 2)) COMMENT '汽油调价幅度(元/吨,首次行=NULL)',
    diesel_change   Nullable(Decimal(12, 2)) COMMENT '柴油调价幅度(元/吨,首次行=NULL)',
    data_source     LowCardinality(String)   DEFAULT 'akshare_alt' COMMENT '数据来源',
    quality_flag    UInt8                    DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts       DateTime64(3, 'UTC')     DEFAULT now() COMMENT '入库时间戳(采集时间锚)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(announce_date)
ORDER BY (announce_date)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "ndrc_fuel_price"
DATABASE = "c1_market"
CATEGORY_ID = "market_ndrc_fuel_price"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(announce_date)"
ORDER_BY = "(announce_date)"

INSERT_COLUMNS = "(announce_date, effective_date, gasoline_price, diesel_price, gasoline_change, diesel_change, data_source, quality_flag)"
