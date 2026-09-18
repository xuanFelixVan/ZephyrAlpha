# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.crypto.hl_liquidation_raw
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.hyperliquid_provider
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] hl_liquidation_raw 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""hl_liquidation_raw（Hyperliquid 清算流原始捕获，只增流水）DDL-as-Code
（category_id: hl_liquidation_raw）.

altdata_line 09 清单 D5 跨资产 H1-3（2026-09-18 夜班施工，st-datapack-20260918）。

源端现实（2026-09-18 实测，PIT 如实披露）：
    - Hyperliquid **无 REST 清算端点**：info type=recentLiquidations 实测 422
      （Failed to deserialize，类型不存在于官方 info-endpoint 文档清单）
    - WS 无公开 liquidation 订阅频道：allLiquidation/liquidation/webData2 实测均
      "Error parsing JSON into valid websocket request"（官方 subscriptions 文档亦无此类型）
    - 官方公开通道唯一可行捕获面 = trades 流：清算单以对手方地址
      0xffffffffffffffffffffffffffffffffffffffff（清算账本专用地址，社区追踪器通行口径）
      出现在 users 字段——本表按该标记落库，is_liquidation=1

采集方式（本班=有界捕获，非守护进程）：
    daily_crypto 档每日一次 bounded WS 捕获（默认 30 分钟窗口，extra.capture_minutes 可调），
    订阅全永续 universe trades 流，过滤清算标记地址逐笔落库；capture_mode 列记录口径。
    **全量 7x24 WS 守护进程留下一班**（altdata_line 09 D5 挂账）——本表当前为逐日
    30 分钟采样口径，非全量清算流，消费侧不得当全量口径使用（已披露）。

心跳行约定：静默窗口（流存活但零清算成交）落一条 coin='__CAPTURE_HEARTBEAT__' 行，
trade_hash 携带 "window/coins/trades_seen" 覆盖台账——①供哨兵 ingest_ts 新鲜度判定
（空表 max() 返回 epoch 会误报断供）；②捕获覆盖审计。消费侧过滤该 coin 前缀即得纯清算行。

表性质：MergeTree 只增流水（tid 全局唯一，ReplacingMergeTree 同 tid 重放幂等去重）。

与既有 crypto 影子线隔离：独立 hl_ 前缀，无撞名。

PIT 双轴：trade_time=事实时间锚（成交时刻）；ingest_ts=采集时间。

引擎选型：ReplacingMergeTree（ORDER BY (coin, trade_time, tid) 幂等），PARTITION 月。
"""

from __future__ import annotations

# category_id: hl_liquidation_raw
# calc_mode: preload

HL_LIQUIDATION_RAW_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.hl_liquidation_raw
(
    trade_time              DateTime64(3, 'UTC')        COMMENT '成交时刻(事实时间锚)',
    coin                    String                      COMMENT 'Hyperliquid 永续币名',
    side                    LowCardinality(String)      COMMENT '吃单方向(B=买/A=卖)',
    px                      Decimal(38, 18)             COMMENT '成交价(USDC)',
    sz                      Decimal(38, 8)              COMMENT '成交量(基础资产)',
    ntl_usd                 Decimal(38, 8)              COMMENT '名义额(USDC;=px×sz 写侧自算)',
    buyer_addr              String                      COMMENT '买方地址(0x…;清算账本地址见 is_liquidation)',
    seller_addr             String                      COMMENT '卖方地址(0x…)',
    is_liquidation          UInt8                       COMMENT '清算标记(1=买卖双方含清算账本地址0xfff…f)',
    tid                     UInt64                      COMMENT '全局成交ID(去重键)',
    trade_hash              String                      COMMENT '成交hash(源排障锚)',
    capture_mode            LowCardinality(String)      DEFAULT 'ws_trades_bounded' COMMENT '捕获口径(ws_trades_bounded=逐日有界窗口采样;full_ws_daemon=7x24守护,未上线)',
    data_source             LowCardinality(String)      DEFAULT 'hyperliquid' COMMENT '数据来源(wss://api.hyperliquid.xyz/ws 官方公开流)',
    quality_flag            UInt8                       DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts               DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳(采集时间锚)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_time)
ORDER BY (coin, trade_time, tid)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "hl_liquidation_raw"
DATABASE = "c1_market"
CATEGORY_ID = "hl_liquidation_raw"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_time)"
ORDER_BY = "(coin, trade_time, tid)"

INSERT_COLUMNS = (
    "(trade_time, coin, side, px, sz, ntl_usd, buyer_addr, seller_addr, is_liquidation, "
    "tid, trade_hash, capture_mode, data_source, quality_flag)"
)

# 清算账本专用对手方地址（社区追踪器通行口径；官方文档未列表，首跑实测留痕见 provider docstring）
LIQUIDATION_BOOK_ADDR = "0x" + "f" * 40
