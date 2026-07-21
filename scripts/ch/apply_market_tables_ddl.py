# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] scripts.ch.apply_market_tables_ddl
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.data.local_replay
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] DDL-as-Code: tick_data DDL 真源为 schemas/categories/market_tick.py; kline_daily/sector_snapshot DDL 内联; apply() 通过 ch_writer.query 执行; verify() 查询 system.tables 验证引擎
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
    - kline_daily DDL 内联（schema 文件待创建，当前从 blueprint §4.2 派生）
    - sector_snapshot DDL 内联（从 sector_snapshot_collector.py 派生）

引擎选型矩阵（设计文档 §5 Phase F）：
    tick_data        → ReplacingMergeTree（tick 天然唯一）
    kline_daily      → ReplacingMergeTree（日线按交易日去重）
    sector_snapshot  → MergeTree（板块快照允许重复）

用法::

    python scripts/ch/apply_market_tables_ddl.py           # 建表 + 验证
    python scripts/ch/apply_market_tables_ddl.py --verify   # 仅验证

退出码：
    0 = 全部一致
    1 = 有不一致
    2 = ClickHouse 不可达
"""
from __future__ import annotations

import sys
import os

# 确保 src/ 在 path 中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

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
    trade_date   Date                    COMMENT '交易日期',
    timestamp    DateTime                COMMENT '时间戳(3秒粒度)',
    symbol       String                  COMMENT '证券代码',
    market_type  LowCardinality(String)  COMMENT '市场类型',
    price        Decimal(18,4)           COMMENT '成交价',
    volume       UInt64                  COMMENT '成交量(股)',
    amount       Decimal(18,2)           COMMENT '成交额(元)',
    direction    LowCardinality(String) DEFAULT '' COMMENT '买卖方向',
    data_source  LowCardinality(String) DEFAULT 'bdpan' COMMENT '数据来源',
    bid_price    Nullable(Decimal(18,4)) COMMENT '买一价',
    ask_price    Nullable(Decimal(18,4)) COMMENT '卖一价',
    bid_volume   Nullable(UInt64)        COMMENT '买一量',
    ask_volume   Nullable(UInt64)        COMMENT '卖一量',
    quality_flag UInt8          DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (market_type, symbol, trade_date, timestamp, price)
SETTINGS index_granularity = 8192
"""

# kline_daily DDL — 真源: blueprint §4.2（schema 文件待创建）
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

# sector_snapshot DDL — 真源: src/zephyr/data/sector_snapshot_collector.py
SECTOR_SNAPSHOT_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.sector_snapshot
(
    trade_date       Date        COMMENT '交易日',
    timestamp        DateTime    COMMENT '快照时间戳',
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
    fetched_at       DateTime    COMMENT '采集时间(UTC)'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (sector_code, timestamp)
"""

# 所有 DDL（按依赖顺序）
_ALL_DDL: list[tuple[str, str]] = [
    ("c1_market.tick_data", TICK_DATA_DDL),
    ("c1_market.kline_daily", KLINE_DAILY_DDL),
    ("c1_market.sector_snapshot", SECTOR_SNAPSHOT_DDL),
]

# 引擎选型矩阵（用于验证）
_EXPECTED_ENGINES: dict[str, str] = {
    "tick_data": "ReplacingMergeTree",
    "kline_daily": "ReplacingMergeTree",
    "sector_snapshot": "MergeTree",
}

_DATABASE = "c1_market"


def apply() -> int:
    """执行所有建表 DDL。"""
    print("=== 创建数据库 ===")
    ch_writer.query(f"CREATE DATABASE IF NOT EXISTS {_DATABASE}")
    print(f"  {_DATABASE} ✓")

    print("\n=== 执行建表 DDL ===")
    for table, ddl in _ALL_DDL:
        print(f"  {table} ...", end=" ")
        ch_writer.query(ddl)
        print("✓")

    print("\n=== 建表完成 ===")
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
