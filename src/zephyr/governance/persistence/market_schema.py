# [BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md | §market.duckdb 8表 Schema 真源
# [MODULE] zephyr.governance.persistence.market_schema
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] duckdb
# [CONSUMERS] 无（market.duckdb 已于2026-07-01废弃，原消费者 database_service.py market 代码已删除；本文件仅作 DDL 真源归档）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] DDL-as-Code 协议——本文件是 market.duckdb 8 表/视图 DDL 唯一真源; market.duckdb 已于2026-07-01废弃（INFRA-DB-005 deleted），本文件仅作 DDL 真源归档保留
# [MODIFY-GUARD] 改 DDL 前必须 git commit 备份 + 红蓝测试验证
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] init_market_schema 幂等；verify_market_schema 返回 (ok, missing)
# [TESTS] tests/io/test_market_duckdb.py (已删除，market.duckdb 于2026-07-01废弃)
# [A_module] module_id=MOD-INF-012 | layer=module | stability=stable | safety=L | ai_autonomy=human_gated
# [TTL] permanent
"""
market.duckdb 业务时序库 Schema DDL（DDL-as-Code 真源）
=========================================================
依据：SH-DB-001 v4.2.0 §market.duckdb 8 表 Schema 真源

物理路径：data/databases/market.duckdb
Safety  : L（DDL 定义，init_market_schema 幂等执行）

表结构（7 表 + 1 视图）
----------------------
 1. tick_data          — 行情 tick（symbol/timestamp/price/volume/bid1/ask1）
 2. orders             — 订单（PK: order_id）
 3. positions          — 持仓（PK: portfolio_id, symbol 复合主键）
 4. risk_snapshots     — 风险快照（PK: snapshot_id）
 5. factor_values      — 因子值
 6. backtest_results   — 回测结果（PK: backtest_id）
 7. backtest_trades    — 回测成交（PK: trade_id）

视图
----
 8. kline_3s           — 3 秒 K 线（从 tick_data 聚合：OHLCV + time_bucket）

安全约束
--------
查询用 DatabaseService.get_market_read_conn()（read_only=True 代码层强制）
写入用 DatabaseService.get_market_conn() + market_write_lock 串行化
DDL 真源：本文件（market_schema.py）
表清单真源：infrastructure_registry.yaml INFRA-DB-005
安全约束真源：database_service.py:104 get_market_read_conn(read_only=True)

DDL 来源
--------
本 DDL 于 2026-07-01 从现有 market.duckdb 反向导出（information_schema.columns +
duckdb_views()），作为 DDL-as-Code 真源归档。字段类型/约束以导出结果为准。
"""

from __future__ import annotations

# Schema 版本（每次 DDL 变更递增）
MARKET_SCHEMA_VERSION = "1.0.0"

# 预期表/视图清单（与 database_service.DatabaseService.EXPECTED_MARKET_TABLES 保持一致）
EXPECTED_MARKET_TABLES = frozenset(
    {
        "tick_data",
        "kline_3s",
        "orders",
        "positions",
        "risk_snapshots",
        "factor_values",
        "backtest_results",
        "backtest_trades",
    }
)

# 7 张表的 CREATE DDL（IF NOT EXISTS 幂等）
# 主键约束从 information_schema.key_column_usage 反向导出
MARKET_TABLE_DDL: dict[str, str] = {
    "tick_data": """CREATE TABLE IF NOT EXISTS tick_data (
    symbol VARCHAR NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    price DOUBLE,
    volume BIGINT,
    amount DOUBLE,
    bid1 DOUBLE,
    ask1 DOUBLE,
    bid_vol1 BIGINT,
    ask_vol1 BIGINT,
    data_source VARCHAR,
    quality_score SMALLINT
)""",
    "orders": """CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR NOT NULL,
    symbol VARCHAR NOT NULL,
    side VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    qty DOUBLE NOT NULL,
    price DOUBLE,
    status VARCHAR NOT NULL,
    strategy_id VARCHAR,
    portfolio_id VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    fill_price DOUBLE,
    fill_qty DOUBLE,
    commission DOUBLE,
    slippage DOUBLE,
    PRIMARY KEY (order_id)
)""",
    "positions": """CREATE TABLE IF NOT EXISTS positions (
    portfolio_id VARCHAR NOT NULL,
    symbol VARCHAR NOT NULL,
    qty DOUBLE NOT NULL,
    avg_cost DOUBLE,
    current_price DOUBLE,
    unrealized_pnl DOUBLE,
    realized_pnl DOUBLE,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY (portfolio_id, symbol)
)""",
    "risk_snapshots": """CREATE TABLE IF NOT EXISTS risk_snapshots (
    snapshot_id INTEGER NOT NULL,
    portfolio_id VARCHAR NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    var_1d DOUBLE,
    var_1d_95 DOUBLE,
    max_drawdown DOUBLE,
    exposure_by_sector VARCHAR,
    margin_usage DOUBLE,
    liquidity_score DOUBLE,
    PRIMARY KEY (snapshot_id)
)""",
    "factor_values": """CREATE TABLE IF NOT EXISTS factor_values (
    factor_id VARCHAR NOT NULL,
    symbol VARCHAR NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    value DOUBLE,
    quality SMALLINT
)""",
    "backtest_results": """CREATE TABLE IF NOT EXISTS backtest_results (
    backtest_id VARCHAR NOT NULL,
    strategy_id VARCHAR NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DOUBLE NOT NULL,
    final_capital DOUBLE,
    total_return DOUBLE,
    sharpe_ratio DOUBLE,
    max_drawdown DOUBLE,
    win_rate DOUBLE,
    total_trades INTEGER,
    parameters VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY (backtest_id)
)""",
    "backtest_trades": """CREATE TABLE IF NOT EXISTS backtest_trades (
    trade_id INTEGER NOT NULL,
    backtest_id VARCHAR NOT NULL,
    symbol VARCHAR NOT NULL,
    side VARCHAR NOT NULL,
    entry_time TIMESTAMP WITH TIME ZONE NOT NULL,
    exit_time TIMESTAMP WITH TIME ZONE,
    entry_price DOUBLE NOT NULL,
    exit_price DOUBLE,
    qty DOUBLE NOT NULL,
    pnl DOUBLE,
    commission DOUBLE,
    PRIMARY KEY (trade_id)
)""",
}

# 1 个视图的 CREATE DDL（CREATE OR REPLACE VIEW 幂等）
# kline_3s 从 tick_data 聚合：3 秒 OHLCV + 成交量/额
# 注：first/last/close/timestamp 为 DuckDB 保留字，需双引号
MARKET_VIEW_DDL: dict[str, str] = {
    "kline_3s": """CREATE OR REPLACE VIEW kline_3s AS
SELECT
    symbol,
    "first"(price) AS open,
    max(price) AS high,
    min(price) AS low,
    "last"(price) AS "close",
    sum(volume) AS volume,
    sum(amount) AS amount,
    time_bucket(CAST('3 seconds' AS INTERVAL), "timestamp") AS ts
FROM tick_data
GROUP BY symbol, ts""",
}

# 执行顺序：先表后视图（视图依赖 tick_data 表）
_INIT_ORDER = list(MARKET_TABLE_DDL.keys()) + list(MARKET_VIEW_DDL.keys())
_ALL_DDL = {**MARKET_TABLE_DDL, **MARKET_VIEW_DDL}


def init_market_schema(conn) -> None:
    """初始化 market.duckdb schema（幂等）。

    遍历 7 表 + 1 视图的 DDL 依次执行。所有 CREATE 加 IF NOT EXISTS / OR REPLACE，
    支持重复执行。执行顺序：先表后视图（kline_3s 依赖 tick_data）。

    Args:
        conn: duckdb.DuckDBPyConnection（读写连接，由调用方负责生命周期）
    """
    for name in _INIT_ORDER:
        conn.execute(_ALL_DDL[name])


def verify_market_schema(conn) -> tuple[bool, list[str]]:
    """校验 market.duckdb schema 完整性。

    对比数据库实际表/视图清单与 EXPECTED_MARKET_TABLES，返回缺失项。

    Args:
        conn: duckdb.DuckDBPyConnection（建议 read_only=True）

    Returns:
        (ok, missing): ok=True 表示 8 表/视图全部存在；missing 为缺失名称列表
    """
    existing = {
        r[0]
        for r in conn.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema='main'"
        ).fetchall()
    }
    missing = sorted(EXPECTED_MARKET_TABLES - existing)
    return (len(missing) == 0, missing)


def get_schema_version() -> str:
    """返回当前 market.duckdb schema 版本。"""
    return MARKET_SCHEMA_VERSION
