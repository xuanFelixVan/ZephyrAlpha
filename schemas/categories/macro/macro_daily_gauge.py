# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.macro.macro_daily_gauge
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] macro_daily_gauge 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""macro_daily_gauge（宏观高频日度宽表：六大电煤耗+生意社商品/能源/建材指数）DDL-as-Code
（category_id: macro_daily_gauge）.

D3 宏观高频第一梯队（altdata_line 09 清单 D3，2026-09-18 夜班施工）。
宏观日频代理指标宽表：沿海六大电库存/日耗/存煤可用天数（发电量与工业开工高频代理）+
生意社商品价格指数/能源指数/建材指数（PPI 高频代理）。

源：
    macro_china_daily_energy          → coal_inventory/daily_consumption/coal_available_days
    macro_china_commodity_price_index → commodity_price_index（2011-12 起，日更）
    macro_china_energy_index          → energy_price_index（日更）
    macro_china_construction_index    → construction_price_index（日更）

源端现实（2026-09-18 实查）：六大电三列止于 2019-06-21（六大电集团停止披露，源端
退役非断供），2016-01~2019-06 历史段保留（牛熊周期回测价值）；表级活性由生意社
三指数维持（日更，T-1 口径），哨兵按整表 max(trade_date) 判。

与 c1_market.macro_data（长表/月频）的关系（查重声明）：
    本表为日频宽表结构化数据集，频率与口径均不同，按骨架分类学判据 2 独立成表。

PIT 双轴：trade_date=事实时间锚（指数发布日）；ingest_ts=采集时间。

引擎选型：
    ReplacingMergeTree（无版本列，重拉幂等去重）。
    PARTITION BY toYYYYMM(trade_date)。
    ORDER BY (trade_date)。
"""

from __future__ import annotations

# category_id: macro_daily_gauge
# calc_mode: preload

MACRO_DAILY_GAUGE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.macro_daily_gauge
(
    trade_date              Date                        COMMENT '统计日(事实时间锚)',
    coal_inventory          Nullable(Decimal(18, 4))    COMMENT '沿海六大电库存(万吨;历史段2016-01~2019-06)',
    daily_consumption       Nullable(Decimal(18, 4))    COMMENT '六大电日耗(万吨;历史段)',
    coal_available_days     Nullable(Decimal(10, 4))    COMMENT '存煤可用天数(天;历史段)',
    commodity_price_index   Nullable(Decimal(18, 4))    COMMENT '生意社商品价格指数(2011-12起)',
    energy_price_index      Nullable(Decimal(18, 4))    COMMENT '生意社能源指数',
    construction_price_index Nullable(Decimal(18, 4))   COMMENT '生意社建材指数',
    data_source             LowCardinality(String)      DEFAULT 'akshare' COMMENT '数据来源',
    quality_flag            UInt8                       DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts               DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳(采集时间锚)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "macro_daily_gauge"
DATABASE = "c1_market"
CATEGORY_ID = "macro_daily_gauge"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(trade_date)"

INSERT_COLUMNS = (
    "(trade_date, coal_inventory, daily_consumption, coal_available_days, "
    "commodity_price_index, energy_price_index, construction_price_index, data_source, quality_flag)"
)
