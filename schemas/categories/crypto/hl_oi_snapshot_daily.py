# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.crypto.hl_oi_snapshot_daily
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.hyperliquid_provider
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] hl_oi_snapshot_daily 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""hl_oi_snapshot_daily（Hyperliquid 全市场持仓/OI 分布快照，日更自积）DDL-as-Code
（category_id: hl_oi_snapshot_daily）.

altdata_line 09 清单 D5 跨资产 H1-4（2026-09-18 夜班施工，st-datapack-20260918）。

**自积起点 2026-09-18：历史不可回补**——同 hl_perp_snapshot_daily，快照维度无历史回补通道。

与 H1-1 行情快照的分表边界（查重声明）：
    同一次 metaAndAssetCtxs 调用的两个正交切面分表存（官方单次调用即返回全部字段，
    两表各自独立任务独立失败域，消费模式不同）：
    - hl_perp_snapshot_daily = 价格/成交量切面（行情）
    - 本表 = 持仓/OI/资金费切面（仓位结构）：open_interest（基础资产口径）+ oi_ntl_usd
      （采集时点 mark_px 换算 USD 名义，自算口径披露）+ 当小时 funding_rate/premium
      + 冲击买卖价（impactPxs，滑点冲击代理）

源（POST https://api.hyperliquid.xyz/info，匿名免费无 key）：
    {"type": "metaAndAssetCtxs"} → assetCtxs 的 openInterest/funding/premium/impactPxs/markPx

PIT 双轴：snapshot_date=事实时间锚；ingest_ts=采集时间。
OI 分布典型消费：全市场 OI 集中度（HHI）、资金费极值币筛选、杠杆拥挤度截面。

引擎选型：ReplacingMergeTree（同 (coin, snapshot_date) 幂等替换），PARTITION 月，ORDER BY (coin, snapshot_date)。
"""

from __future__ import annotations

# category_id: hl_oi_snapshot_daily
# calc_mode: preload

HL_OI_SNAPSHOT_DAILY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.hl_oi_snapshot_daily
(
    snapshot_date           Date                        COMMENT '快照UTC日(事实时间锚;自积起点2026-09-18,历史不可回补)',
    coin                    String                      COMMENT 'Hyperliquid 永续币名',
    open_interest           Nullable(Decimal(38, 8))    COMMENT '未平仓量(基础资产口径,源 openInterest)',
    oi_ntl_usd              Nullable(Decimal(38, 8))    COMMENT '未平仓名义(USDC;=open_interest×mark_px 采集时点自算,口径披露)',
    funding_rate            Nullable(Decimal(28, 14))   COMMENT '当小时资金费率(源 funding,小时口径未年化)',
    premium                 Nullable(Decimal(28, 14))   COMMENT '标记价溢价(源 premium)',
    impact_bid_px           Nullable(Decimal(38, 18))   COMMENT '冲击买价(impactPxs[0],吃单滑点代理)',
    impact_ask_px           Nullable(Decimal(38, 18))   COMMENT '冲击卖价(impactPxs[1])',
    mark_px                 Nullable(Decimal(38, 18))   COMMENT '标记价(USDC;OI 换算锚,快照时点)',
    data_source             LowCardinality(String)      DEFAULT 'hyperliquid' COMMENT '数据来源(api.hyperliquid.xyz 官方info,免费无key)',
    quality_flag            UInt8                       DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts               DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳(采集时间锚)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(snapshot_date)
ORDER BY (coin, snapshot_date)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "hl_oi_snapshot_daily"
DATABASE = "c1_market"
CATEGORY_ID = "hl_oi_snapshot_daily"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(snapshot_date)"
ORDER_BY = "(coin, snapshot_date)"

INSERT_COLUMNS = (
    "(snapshot_date, coin, open_interest, oi_ntl_usd, funding_rate, premium, "
    "impact_bid_px, impact_ask_px, mark_px, data_source, quality_flag)"
)
