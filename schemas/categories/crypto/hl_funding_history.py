# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.crypto.hl_funding_history
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.hyperliquid_provider
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] hl_funding_history 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""hl_funding_history（Hyperliquid 资金费率逐小时历史，长表）DDL-as-Code
（category_id: hl_funding_history）.

altdata_line 09 清单 D5 跨资产 H1-2（2026-09-18 夜班施工，st-datapack-20260918）。

源（POST https://api.hyperliquid.xyz/info，匿名免费无 key）：
    {"type": "fundingHistory", "coin": <coin>, "startTime": <ms>, "endTime": <ms>}
    单页上限 500 行，翻页=上次末行 time 作下次 startTime（官方通用分页规则）。

回溯能力（2026-09-18 实测）：BTC 段 startTime=0 可回至 2023-05-12（首笔 funding 事件），
与快照类不同，本表**历史可回补**——首跑已按全市场逐币 from-inception 深回溯落库，
此后 daily_crypto 档每日增量（lookback 3 天窗口幂等重放，ReplacingMergeTree 同键去重）。
回补深度如实：各币起于各自上线首笔（BTC 2023-05 起，后上币依其上市时间）。

口径披露（PIT 如实）：
    - funding_rate 为小时费率（未年化、未 ×8）， Hyperliquid 原生小时结算口径
    - coin 名为当期 universe 名（改名/迁移事件不做历史重写，源无此映射）
    - premium 同源字段一并落库（funding=premium+利差 clamp 的输入侧留痕）

与既有 crypto 影子线隔离：crypto_kline_daily（币安现货日线）之外独立 hl_ 前缀，无撞名。

PIT 双轴：funding_time=事实时间锚（费率生效小时）；ingest_ts=采集时间。

引擎选型：ReplacingMergeTree（同 (coin, funding_time) 幂等替换），PARTITION 月，ORDER BY (coin, funding_time)。
"""

from __future__ import annotations

# category_id: hl_funding_history
# calc_mode: preload

HL_FUNDING_HISTORY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.hl_funding_history
(
    coin                    String                      COMMENT 'Hyperliquid 永续币名',
    funding_time            DateTime64(3, 'UTC')        COMMENT '费率生效时刻(事实时间锚,小时口径)',
    funding_rate            Nullable(Decimal(28, 14))   COMMENT '小时资金费率(未年化,Hyperliquid 原生口径)',
    premium                 Nullable(Decimal(28, 14))   COMMENT '标记价溢价(源 premium)',
    data_source             LowCardinality(String)      DEFAULT 'hyperliquid' COMMENT '数据来源(api.hyperliquid.xyz 官方info,免费无key)',
    quality_flag            UInt8                       DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts               DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳(采集时间锚)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(funding_time)
ORDER BY (coin, funding_time)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "hl_funding_history"
DATABASE = "c1_market"
CATEGORY_ID = "hl_funding_history"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(funding_time)"
ORDER_BY = "(coin, funding_time)"

INSERT_COLUMNS = "(coin, funding_time, funding_rate, premium, data_source, quality_flag)"
