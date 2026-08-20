# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] scripts.ch.apply_market_tables_ddl
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.data.local_replay
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] DDL-as-Code: tick_data DDL 真源为 schemas/categories/market_tick.py; kline_daily DDL 真源为 schemas/categories/market_kline_daily.py; auction_book DDL 真源为 schemas/categories/market_auction_book.py; sector_snapshot DDL 真源为 schemas/categories/market_sector_snapshot.py; apply() 通过 ch_writer.query 执行; verify() 查询 system.tables 验证引擎
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH不可达->打印错误+退出码2; 引擎不匹配->列出差异+退出码1; 全部匹配->退出码0
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: 部署脚本与 schema 文件 DDL 内容相同但用途不同(apply vs SSoT)
"""ClickHouse c1_market 建表 DDL 部署 + 引擎验证脚本（Phase F）。

DDL-as-Code 模式：
    - tick_data DDL 真源为 schemas/categories/market_tick.py（本脚本导入引用）
    - kline_daily DDL 真源为 schemas/categories/market_kline_daily.py（本脚本导入引用）
    - auction_book DDL 真源为 schemas/categories/market_auction_book.py（本脚本导入引用）
    - sector_snapshot DDL 真源为 schemas/categories/market_sector_snapshot.py（本脚本导入引用）

引擎选型矩阵（设计文档 §5 Phase F，裁定 #ARCH-SSOT-REFERENCE-INTEGRITY-001 Phase F 治本）：
    tick_data        → ReplacingMergeTree（tick 天然唯一）
    kline_daily      → ReplacingMergeTree（日线按交易日去重）
    auction_book     → ReplacingMergeTree（集合竞价高频推送，按 (symbol,trade_date,timestamp) 去重）
    sector_snapshot  → ReplacingMergeTree（板块快照高频推送，按 (sector_code,timestamp) 去重）

用法::

    python scripts/ch/apply_market_tables_ddl.py           # 建表 + 验证
    python scripts/ch/apply_market_tables_ddl.py --verify   # 仅验证

退出码：
    0 = 全部一致
    1 = 有不一致
    2 = ClickHouse 不可达
"""

from __future__ import annotations

import os
import sys

# 确保 src/ 在 path 中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
# 仓根入 path（schemas/categories/*.py DDL-as-Code 真源导入前提；
# 此前缺失导致 try/except 内联 fallback 成为事实运行时——真源漂移温床，JOB-077 治本）
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from zephyr.data import ch_writer

# ========== DDL 定义 ==========

# tick_data DDL — 真源: schemas/categories/market_tick.py
try:
    from schemas.categories.market_tick import TICK_DATA_DDL
except ImportError:
    # fallback: 内联定义（与 schema 文件保持一致）
    TICK_DATA_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.tick_data
(
    trade_date    Date                    COMMENT '交易日期',
    timestamp     DateTime64(3, 'Asia/Shanghai') COMMENT '时间戳(3秒粒度)',
    recorded_time DateTime64(3, 'UTC')  DEFAULT now() COMMENT '录制器本地接收时间(用于延迟分析)',
    symbol        String                  COMMENT '证券代码',
    market_type   LowCardinality(String)  COMMENT '市场类型',
    price         Decimal(18,4)           COMMENT '成交价',
    volume        UInt64                  COMMENT '成交量(股)',
    amount        Decimal(18,2)           COMMENT '成交额(元)',
    direction     LowCardinality(String) DEFAULT '' COMMENT '买卖方向',
    data_source   LowCardinality(String) DEFAULT 'bdpan' COMMENT '数据来源',
    bid_price     Nullable(Decimal(18,4)) COMMENT '买一价',
    ask_price     Nullable(Decimal(18,4)) COMMENT '卖一价',
    bid_volume    Nullable(UInt64)        COMMENT '买一量',
    ask_volume    Nullable(UInt64)        COMMENT '卖一量',
    quality_flag  UInt8          DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (market_type, symbol, trade_date, timestamp, price)
SETTINGS index_granularity = 8192
"""

# l2_tick DDL — 真源: schemas/categories/market_l2_tick.py（2026-07-28 建表，#ARCH-DATA-PIPELINE-001）
try:
    from schemas.categories.market_l2_tick import L2_TICK_DDL
except ImportError:
    L2_TICK_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.l2_tick
(
    trade_date    Date,
    timestamp     DateTime64(3, 'Asia/Shanghai'),
    recorded_time DateTime64(3, 'UTC')  DEFAULT now(),
    symbol        String,
    market_type   LowCardinality(String)  DEFAULT '',
    price         Decimal(18,4),
    volume        UInt64,
    amount        Decimal(18,2),
    direction     LowCardinality(String)  DEFAULT '',
    bid_price     Nullable(Decimal(18,4)),
    ask_price     Nullable(Decimal(18,4)),
    bid_volume    Nullable(UInt64),
    ask_volume    Nullable(UInt64),
    data_source   LowCardinality(String)  DEFAULT 'miniqmt',
    quality_flag  UInt8          DEFAULT 1,
    ingest_ts     DateTime64(3, 'UTC') DEFAULT now(),
    INDEX idx_ts timestamp TYPE minmax GRANULARITY 1,
    INDEX idx_symbol symbol TYPE set(10000) GRANULARITY 4
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (market_type, symbol, trade_date, timestamp, price)
SETTINGS index_granularity = 8192
"""

# kline_daily DDL — 真源: schemas/categories/market_kline_daily.py
try:
    from schemas.categories.market_kline_daily import KLINE_DAILY_DDL
except ImportError:
    # fallback: 内联定义（与 schema 文件保持一致）
    KLINE_DAILY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.kline_daily
(
    trade_date   Date           COMMENT '交易日期',
    symbol       String         COMMENT '证券代码',
    open         Decimal(18,4)  COMMENT '开盘价',
    high         Decimal(18,4)  COMMENT '最高价',
    low          Decimal(18,4)  COMMENT '最低价',
    close        Decimal(18,4)  COMMENT '收盘价',
    volume       UInt64         COMMENT '成交量(股)',
    amount       Decimal(18,2)  COMMENT '成交额(元)',
    amplitude    Decimal(18,4)  DEFAULT 0 COMMENT '振幅(%)',
    pct_change   Decimal(18,4)  DEFAULT 0 COMMENT '涨跌幅(%)',
    change       Decimal(18,4)  DEFAULT 0 COMMENT '涨跌额(元)',
    turnover     Decimal(18,4)  DEFAULT 0 COMMENT '换手率(%)',
    adj_factor   Decimal(18,8)  DEFAULT 1 COMMENT '复权因子',
    market_type  LowCardinality(String) DEFAULT 'A_share' COMMENT '市场类型',
    data_source  LowCardinality(String)  COMMENT '数据来源',
    quality_flag UInt8          DEFAULT 1  COMMENT '质量标记'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
SETTINGS index_granularity = 8192
"""

# kline_etf_daily DDL — 真源: schemas/categories/market_kline_etf_daily.py
try:
    from schemas.categories.market_kline_etf_daily import MARKET_KLINE_ETF_DAILY_DDL
except ImportError:
    # fallback: 内联定义（与 schema 文件保持一致）
    MARKET_KLINE_ETF_DAILY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.kline_etf_daily
(
    trade_date   Date           COMMENT '交易日期',
    symbol       String         COMMENT 'ETF代码',
    open         Decimal(18,4)  COMMENT '开盘价',
    high         Decimal(18,4)  COMMENT '最高价',
    low          Decimal(18,4)  COMMENT '最低价',
    close        Decimal(18,4)  COMMENT '收盘价',
    volume       UInt64         COMMENT '成交量(份)',
    amount       Decimal(18,2)  COMMENT '成交额(元)',
    pct_change   Decimal(18,4)  DEFAULT 0 COMMENT '涨跌幅(%)',
    amplitude    Decimal(18,4)  DEFAULT 0 COMMENT '振幅(%)',
    data_source  LowCardinality(String) DEFAULT 'miniqmt' COMMENT '数据来源',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
"""

# auction_book DDL — 真源: schemas/categories/market_auction_book.py
try:
    from schemas.categories.market_auction_book import AUCTION_BOOK_DDL
except ImportError:
    # fallback: 内联定义（与 schema 文件保持一致）
    AUCTION_BOOK_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.auction_book
(
    trade_date   Date           COMMENT '交易日期',
    timestamp    DateTime64(3, 'Asia/Shanghai') COMMENT '快照时间戳(精确到秒)',
    symbol       String         COMMENT '证券代码',
    last_price   Decimal(18,4)  COMMENT '最新成交价',
    volume       UInt64         COMMENT '累计成交量(手)',
    amount       Decimal(18,2)  COMMENT '累计成交额(元)',
    open         Decimal(18,4)  COMMENT '当日开盘价',
    high         Decimal(18,4)  COMMENT '当日最高价',
    low          Decimal(18,4)  COMMENT '当日最低价',
    pre_close    Decimal(18,4)  COMMENT '昨收价',
    upper_limit  Decimal(18,4)  COMMENT '涨停价',
    lower_limit  Decimal(18,4)  COMMENT '跌停价',
    bid_price1   Decimal(18,4)  COMMENT '买一价',
    bid_price2   Decimal(18,4)  COMMENT '买二价',
    bid_price3   Decimal(18,4)  COMMENT '买三价',
    bid_price4   Decimal(18,4)  COMMENT '买四价',
    bid_price5   Decimal(18,4)  COMMENT '买五价',
    bid_volume1  UInt64         COMMENT '买一量(手)',
    bid_volume2  UInt64         COMMENT '买二量(手)',
    bid_volume3  UInt64         COMMENT '买三量(手)',
    bid_volume4  UInt64         COMMENT '买四量(手)',
    bid_volume5  UInt64         COMMENT '买五量(手)',
    ask_price1   Decimal(18,4)  COMMENT '卖一价',
    ask_price2   Decimal(18,4)  COMMENT '卖二价',
    ask_price3   Decimal(18,4)  COMMENT '卖三价',
    ask_price4   Decimal(18,4)  COMMENT '卖四价',
    ask_price5   Decimal(18,4)  COMMENT '卖五价',
    ask_volume1  UInt64         COMMENT '卖一量(手)',
    ask_volume2  UInt64         COMMENT '卖二量(手)',
    ask_volume3  UInt64         COMMENT '卖三量(手)',
    ask_volume4  UInt64         COMMENT '卖四量(手)',
    ask_volume5  UInt64         COMMENT '卖五量(手)',
    data_source  LowCardinality(String) COMMENT '数据来源(miniQMT)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date, timestamp)
SETTINGS index_granularity = 8192
"""

# sector_snapshot DDL — 真源: schemas/categories/market_sector_snapshot.py
# 引擎治本迁移（#ARCH-SSOT-REFERENCE-INTEGRITY-001 Phase F）：
# 原 MergeTree（板块快照允许重复）→ ReplacingMergeTree（高频推送按 (sector_code,timestamp) 去重）
# 原因：sector_snapshot 是高频表（30秒轮询+99只推送），MergeTree 写前 DELETE 留 mutations 累积；
# ReplacingMergeTree 直接 INSERT + 后台合并去重，符合 ch_writer.py §7.3 幂等性策略首选。
# Phase 2 治本（2026-07-22）：DDL 从 sector_snapshot_collector.py 内联迁移到独立 schema 文件，
# 消除双真源（本脚本与 collector 共用同一 schema 文件作为 SSoT）。
try:
    from schemas.categories.market_sector_snapshot import SECTOR_SNAPSHOT_DDL
except ImportError:
    # fallback: 内联定义（与 schema 文件保持一致）
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
    fetched_at       DateTime64(3, 'UTC') COMMENT '采集时间(UTC)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (sector_code, timestamp)
"""

# cross_validation_log DDL — 真源: schemas/categories/cross_validation_log.py (P1-4)
try:
    from schemas.categories.cross_validation_log import CROSS_VALIDATION_LOG_DDL
except ImportError:
    CROSS_VALIDATION_LOG_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.cross_validation_log
(
    check_time     DateTime64(3, 'UTC')        COMMENT '校验执行时间',
    check_date     Date                    COMMENT '校验数据日期',
    symbol         String                  COMMENT '证券代码',
    metric         LowCardinality(String)  COMMENT '校验指标',
    primary_value  String                  COMMENT '主源值',
    backup_value   String                  COMMENT '备源值',
    deviation      Decimal(18,6)           COMMENT '偏差',
    threshold      Decimal(18,6)           COMMENT '偏差阈值',
    status         LowCardinality(String)  COMMENT '校验结果(pass/warn/fail)',
    detail         String                  DEFAULT '' COMMENT '详细信息'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(check_date)
ORDER BY (check_date, symbol, metric, check_time)
"""

# hog_spot_index DDL — 真源: schemas/categories/market_hog_spot_index.py (2026-07-29 生猪价格接入)
try:
    from schemas.categories.market_hog_spot_index import HOG_SPOT_INDEX_DDL
except ImportError:
    HOG_SPOT_INDEX_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.hog_spot_index
(
    trade_date          Date           COMMENT '统计日期(周度)',
    index_value         Decimal(18,4)  COMMENT '生猪现货价格指数',
    ma_4m               Float64        COMMENT '4个月均线',
    ma_6m               Float64        COMMENT '6个月均线',
    ma_12m              Float64        COMMENT '12个月均线',
    presale_avg_price   Decimal(18,4)  COMMENT '预售均价(元/公斤)',
    deal_avg_price      Decimal(18,4)  COMMENT '成交均价(元/公斤)',
    deal_avg_weight     Float64        COMMENT '成交均重(公斤)',
    ingest_ts           DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY (trade_date)
SETTINGS index_granularity = 8192
"""

# hog_futures_core DDL — 真源: schemas/categories/market_hog_futures_core.py
try:
    from schemas.categories.market_hog_futures_core import HOG_FUTURES_CORE_DDL
except ImportError:
    HOG_FUTURES_CORE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.hog_futures_core
(
    trade_date    Date           COMMENT '交易日期',
    value         Decimal(18,4)  COMMENT '生猪期货核心价(元/公斤)',
    ingest_ts     DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY (trade_date)
SETTINGS index_granularity = 8192
"""

# hog_province_spot DDL — 真源: schemas/categories/market_hog_province_spot.py
try:
    from schemas.categories.market_hog_province_spot import HOG_PROVINCE_SPOT_DDL
except ImportError:
    HOG_PROVINCE_SPOT_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.hog_province_spot
(
    trade_date    Date           COMMENT '交易日期(快照日)',
    province      String         COMMENT '省份',
    price         Decimal(18,4)  COMMENT '生猪现价(元/公斤)',
    change        Float64        COMMENT '涨跌幅(元/公斤)',
    ingest_ts     DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, province)
SETTINGS index_granularity = 8192
"""

# JOB-077 市场元数据与约束接入（DS-081~083，2026-08-15）— 真源: schemas/categories/ 同名文件
# 不内联 fallback：DDL 部署必须 fail-closed（导入失败即报错），防止静默使用漂移副本建错表
# tracker #114 / 37号 §3.2a（2026-08-17 AI-IPO-001）：IPO 日历/募资规模（巨潮新股列表）
from schemas.categories.market_ipo_calendar import IPO_CALENDAR_DDL
from schemas.categories.market_stk_limit import STK_LIMIT_DDL
from schemas.categories.market_suspend import SUSPEND_DDL
from schemas.categories.meta_stock_basic import STOCK_BASIC_DDL

# 所有 DDL（按依赖顺序）
_ALL_DDL: list[tuple[str, str]] = [
    ("c1_market.tick_data", TICK_DATA_DDL),
    ("c1_market.l2_tick", L2_TICK_DDL),
    ("c1_market.kline_daily", KLINE_DAILY_DDL),
    ("c1_market.kline_etf_daily", MARKET_KLINE_ETF_DAILY_DDL),
    ("c1_market.auction_book", AUCTION_BOOK_DDL),
    ("c1_market.sector_snapshot", SECTOR_SNAPSHOT_DDL),
    ("c1_market.cross_validation_log", CROSS_VALIDATION_LOG_DDL),
    ("c1_market.hog_spot_index", HOG_SPOT_INDEX_DDL),
    ("c1_market.hog_futures_core", HOG_FUTURES_CORE_DDL),
    ("c1_market.hog_province_spot", HOG_PROVINCE_SPOT_DDL),
    # JOB-077 市场元数据与约束接入（DS-081~083，2026-08-15）
    ("c1_market.stock_basic", STOCK_BASIC_DDL),
    ("c1_market.stk_limit", STK_LIMIT_DDL),
    ("c1_market.suspend", SUSPEND_DDL),
    # tracker #114 / 37号 §3.2a（2026-08-17 AI-IPO-001）
    ("c1_market.ipo_calendar", IPO_CALENDAR_DDL),
]

# 增量迁移（ALTER TABLE ADD COLUMN IF NOT EXISTS）
# 用于已存在的表新增列，CREATE TABLE IF NOT EXISTS 不会修改已存在的表结构
# 每项: (表名, ALTER SQL)
_MIGRATIONS: list[tuple[str, str]] = [
    # P0-1 双时间戳（2026-07-22）: tick_data 新增 recorded_time 列
    (
        "c1_market.tick_data",
        "ALTER TABLE c1_market.tick_data "
        "ADD COLUMN IF NOT EXISTS recorded_time DateTime64(3, 'UTC') DEFAULT now() "
        "COMMENT '录制器本地接收时间(用于延迟分析)' AFTER timestamp",
    ),
]

# 引擎选型矩阵（用于验证）
_EXPECTED_ENGINES: dict[str, str] = {
    "tick_data": "ReplacingMergeTree",
    "l2_tick": "ReplacingMergeTree",
    "kline_daily": "ReplacingMergeTree",
    "kline_etf_daily": "ReplacingMergeTree",
    "auction_book": "ReplacingMergeTree",
    "sector_snapshot": "ReplacingMergeTree",
    "cross_validation_log": "MergeTree",
    "hog_spot_index": "ReplacingMergeTree",
    "hog_futures_core": "ReplacingMergeTree",
    "hog_province_spot": "ReplacingMergeTree",
    # JOB-077（DS-081~083，2026-08-15）
    "stock_basic": "ReplacingMergeTree",
    "stk_limit": "ReplacingMergeTree",
    "suspend": "ReplacingMergeTree",
    "ipo_calendar": "ReplacingMergeTree",
}

_DATABASE = "c1_market"


def apply() -> int:
    """执行所有建表 DDL + 增量迁移。"""
    print("=== 创建数据库 ===")
    ch_writer.query(f"CREATE DATABASE IF NOT EXISTS {_DATABASE}")
    print(f"  {_DATABASE} ✓")

    print("\n=== 执行建表 DDL ===")
    for table, ddl in _ALL_DDL:
        print(f"  {table} ...", end=" ")
        ch_writer.query(ddl)
        print("✓")

    print("\n=== 执行增量迁移（ALTER TABLE） ===")
    for table, sql in _MIGRATIONS:
        print(f"  {table} ...", end=" ")
        ch_writer.query(sql)
        print("✓")

    print("\n=== 建表 + 迁移完成 ===")
    return 0


def verify() -> int:
    """查询 CH 表引擎并与预期对比。"""
    sql = f"SELECT name, engine FROM system.tables WHERE database = '{_DATABASE}' ORDER BY name"
    raw = ch_writer.query(sql)

    if not raw.strip():
        print(f"[ERROR] 查询 system.tables 返回空——ClickHouse 可能不可达或库 {_DATABASE} 不存在")
        return 2

    actual: dict[str, str] = {}
    for line in raw.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) == 2:
            actual[parts[0]] = parts[1]

    print(f"{'表名':<25} {'预期引擎':<25} {'实际引擎':<25} {'is_replacing':<15} {'状态'}")
    print("-" * 100)

    all_match = True
    for table, expected_prefix in _EXPECTED_ENGINES.items():
        engine = actual.get(table, "")
        if not engine:
            print(f"{table:<25} {expected_prefix:<25} {'(不存在)':<25} {'':<15} ❌ 表不存在")
            all_match = False
            continue

        is_replacing = ch_writer.is_replacing_engine(f"{_DATABASE}.{table}")
        matches = engine.startswith(expected_prefix)
        status = "✅ 一致" if matches else "❌ 不一致"
        if not matches:
            all_match = False
        print(f"{table:<25} {expected_prefix:<25} {engine:<25} {str(is_replacing):<15} {status}")

    extra = set(actual.keys()) - set(_EXPECTED_ENGINES.keys())
    for table in sorted(extra):
        engine = actual[table]
        is_replacing = ch_writer.is_replacing_engine(f"{_DATABASE}.{table}")
        print(f"{table:<25} {'(未预期)':<25} {engine:<25} {str(is_replacing):<15} ⚠️ 未在选型矩阵中")

    print("-" * 100)
    if all_match:
        print("[OK] 所有表引擎与设计一致")
        return 0
    print("[FAIL] 存在引擎不一致，请检查")
    return 1


def main() -> int:
    """入口：默认 apply + verify，--verify 仅验证。"""
    if "--verify" in sys.argv:
        return verify()
    rc = apply()
    if rc != 0:
        return rc
    print()
    return verify()


if __name__ == "__main__":
    sys.exit(main())
