# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.crypto.hl_perp_snapshot_daily
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.hyperliquid_provider
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] hl_perp_snapshot_daily 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""hl_perp_snapshot_daily（Hyperliquid 全市场永续行情快照，日更自积）DDL-as-Code
（category_id: hl_perp_snapshot_daily）.

altdata_line 09 清单 D5 跨资产 H1-1（2026-09-18 夜班施工，st-datapack-20260918）。

**自积起点 2026-09-18：历史不可回补**——本表为每日采集时点的全市场快照（snapshot_ts
维度），Hyperliquid 官方 info API 不提供历史快照回补，晚一天接入少一天数据，故 D5 最先点火。
每天 08:4x（daily_crypto 档，北京=UTC+8，即 UTC 00:4x）采一次 metaAndAssetCtxs
（官方 docs.hyperliquid.xyz/for-developers/api/info-endpoint/perpetuals），
全永续市场逐币一行（首跑 234 币，含 isDelisted 行）。

源（POST https://api.hyperliquid.xyz/info，匿名免费无 key）：
    {"type": "metaAndAssetCtxs"} → meta.universe（szDecimals/maxLeverage/isDelisted）
                                 + assetCtxs（markPx/oraclePx/midPx/prevDayPx/dayNtlVlm/dayBaseVlm）

口径披露（PIT 如实）：
    - day_ntl_vlm/day_base_vlm = 采集时点滚动 24 小时口径（非 UTC 自然日累计）
    - mid_px 可为 null（停牌/无成交币）
    - 宇宙=当日接口返回的全量永续（新币自动进入、下架币 is_delisted=1 保留行）

与既有 crypto 影子线隔离（查重声明）：
    crypto_kline_daily=币安现货 Top-50 日线（K 线维度）；本表=Hyperliquid 全永续市场
    快照（快照维度，交易所/口径/结构均不同），按骨架分类学判据 2 独立成表，hl_ 前缀不撞名。

PIT 双轴：snapshot_date=事实时间锚（快照 UTC 日）；ingest_ts=采集时间。

引擎选型：
    ReplacingMergeTree（无版本列，同 (coin, snapshot_date) 重跑幂等替换）。
    PARTITION BY toYYYYMM(snapshot_date)。
    ORDER BY (coin, snapshot_date)。
"""

from __future__ import annotations

# category_id: hl_perp_snapshot_daily
# calc_mode: preload

HL_PERP_SNAPSHOT_DAILY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.hl_perp_snapshot_daily
(
    snapshot_date           Date                        COMMENT '快照UTC日(事实时间锚;自积起点2026-09-18,历史不可回补)',
    coin                    String                      COMMENT 'Hyperliquid 永续币名(如 BTC/PURR/USDC)',
    sz_decimals             UInt8                       COMMENT '数量小数位(meta.universe.szDecimals)',
    max_leverage            UInt16                      COMMENT '最大杠杆倍数(meta.universe.maxLeverage)',
    mark_px                 Nullable(Decimal(38, 18))   COMMENT '标记价(USDC)',
    oracle_px               Nullable(Decimal(38, 18))   COMMENT '预言机价(USDC)',
    mid_px                  Nullable(Decimal(38, 18))   COMMENT '盘口中价(USDC;无成交可为null)',
    prev_day_px             Nullable(Decimal(38, 18))   COMMENT '前一日价(USDC)',
    day_ntl_vlm             Nullable(Decimal(38, 8))    COMMENT '滚动24h成交额(USDC;采集时点口径非自然日)',
    day_base_vlm            Nullable(Decimal(38, 8))    COMMENT '滚动24h成交量(基础资产)',
    is_delisted             UInt8                       DEFAULT 0 COMMENT '下架标记(meta.universe.isDelisted;1=已下架)',
    data_source             LowCardinality(String)      DEFAULT 'hyperliquid' COMMENT '数据来源(api.hyperliquid.xyz 官方info,免费无key)',
    quality_flag            UInt8                       DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts               DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳(采集时间锚)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(snapshot_date)
ORDER BY (coin, snapshot_date)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "hl_perp_snapshot_daily"
DATABASE = "c1_market"
CATEGORY_ID = "hl_perp_snapshot_daily"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(snapshot_date)"
ORDER_BY = "(coin, snapshot_date)"

INSERT_COLUMNS = (
    "(snapshot_date, coin, sz_decimals, max_leverage, mark_px, oracle_px, mid_px, prev_day_px, "
    "day_ntl_vlm, day_base_vlm, is_delisted, data_source, quality_flag)"
)
