"""
DM-100018: market.duckdb端到端功能测试
覆盖tick_data/kline_3s/orders/positions/backtest_results/backtest_trades/risk_snapshots/factor_values
"""

import sys
import time
from datetime import datetime, timedelta

import duckdb

from zephyr.shared.io.paths import REPO_ROOT, DB_PATH  # 仓库根真源（SSoT：zephyr.shared.io.paths）

DB_PATH = str(REPO_ROOT / "data" / "databases" / "market.duckdb")


def test_all():
    conn = duckdb.connect(DB_PATH)
    passed = 0
    failed = 0

    def check(name, condition, detail=""):
        nonlocal passed, failed
        if condition:
            passed += 1
            print(f"  PASS: {name}")
        else:
            failed += 1
            print(f"  FAIL: {name} - {detail}")

    # === 1. tick_data ===
    print("\n=== 1. tick_data ===")
    base_time = datetime(2026, 6, 12, 9, 30, 0)
    ticks = []
    for i in range(100):
        ts = (base_time + timedelta(seconds=i * 3)).isoformat()
        ticks.append(
            (
                "600519.SH",
                ts,
                1800.0 + i * 0.1,
                100 + i * 10,
                180000.0 + i * 10000,
                1799.5 + i * 0.1,
                1800.5 + i * 0.1,
                500 + i * 10,
                600 + i * 10,
                "test",
                100,
            )
        )

    conn.executemany(
        """INSERT INTO tick_data
        (symbol, timestamp, price, volume, amount, bid1, ask1, bid_vol1, ask_vol1, data_source, quality_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        ticks,
    )

    count = conn.execute("SELECT COUNT(*) FROM tick_data").fetchone()[0]
    check("tick_data INSERT 100 rows", count >= 100, f"got {count}")

    # === 2. kline_3s 视图 ===
    print("\n=== 2. kline_3s view ===")
    kline = conn.execute("SELECT * FROM kline_3s WHERE symbol='600519.SH' ORDER BY ts LIMIT 5").fetchall()
    check("kline_3s query", len(kline) > 0, f"got {len(kline)} rows")
    if kline:
        check("kline_3s has OHLCV", kline[0][1] is not None and kline[0][5] is not None)

    # === 3. orders ===
    print("\n=== 3. orders ===")
    now = datetime.now().isoformat()
    conn.execute(
        """INSERT INTO orders
        (order_id, symbol, side, type, qty, price, status, strategy_id, portfolio_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        ("ORD-001", "600519.SH", "BUY", "LIMIT", 100.0, 1800.0, "SUBMITTED", "STRAT-001", "PF-001", now, now),
    )
    conn.commit()

    order = conn.execute("SELECT * FROM orders WHERE order_id='ORD-001'").fetchone()
    check("orders INSERT+SELECT", order is not None)

    conn.execute(
        "UPDATE orders SET status='FILLED', fill_price=1800.5, fill_qty=100.0, updated_at=? WHERE order_id='ORD-001'",
        (now,),
    )
    conn.commit()
    status = conn.execute("SELECT status FROM orders WHERE order_id='ORD-001'").fetchone()[0]
    check("orders UPDATE status", status == "FILLED")

    # === 4. positions ===
    print("\n=== 4. positions ===")
    conn.execute(
        """INSERT INTO positions
        (portfolio_id, symbol, qty, avg_cost, current_price, unrealized_pnl, realized_pnl, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        ("PF-001", "600519.SH", 100.0, 1800.0, 1850.0, 5000.0, 0.0, now),
    )
    conn.commit()
    pos = conn.execute("SELECT * FROM positions WHERE portfolio_id='PF-001' AND symbol='600519.SH'").fetchone()
    check("positions INSERT+SELECT", pos is not None)

    # === 5. backtest_results + backtest_trades ===
    print("\n=== 5. backtest_results + backtest_trades ===")
    conn.execute(
        """INSERT INTO backtest_results
        (backtest_id, strategy_id, start_date, end_date, initial_capital, final_capital,
         total_return, sharpe_ratio, max_drawdown, win_rate, total_trades, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        ("BT-001", "STRAT-001", "2025-01-01", "2026-06-01", 1000000.0, 1250000.0, 0.25, 1.5, 0.12, 0.55, 200, now),
    )
    conn.commit()
    bt = conn.execute("SELECT * FROM backtest_results WHERE backtest_id='BT-001'").fetchone()
    check("backtest_results INSERT+SELECT", bt is not None)

    conn.execute(
        """INSERT INTO backtest_trades
        (trade_id, backtest_id, symbol, side, entry_time, exit_time, entry_price, exit_price, qty, pnl, commission)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            1,
            "BT-001",
            "600519.SH",
            "BUY",
            "2025-06-01T09:30:00",
            "2025-06-05T15:00:00",
            1800.0,
            1900.0,
            100.0,
            10000.0,
            50.0,
        ),
    )
    conn.commit()
    trade = conn.execute("SELECT * FROM backtest_trades WHERE backtest_id='BT-001'").fetchone()
    check("backtest_trades INSERT+SELECT", trade is not None)

    # 关联查询
    result = conn.execute("""SELECT bt.backtest_id, bt.total_return, t.pnl
        FROM backtest_results bt JOIN backtest_trades t ON bt.backtest_id = t.backtest_id
        WHERE bt.backtest_id='BT-001'""").fetchone()
    check("backtest JOIN query", result is not None and result[1] == 0.25)

    # === 6. risk_snapshots ===
    print("\n=== 6. risk_snapshots ===")
    conn.execute(
        """INSERT INTO risk_snapshots
        (snapshot_id, portfolio_id, timestamp, var_1d, var_1d_95, max_drawdown, margin_usage, liquidity_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (1, "PF-001", now, 50000.0, 75000.0, 0.08, 0.3, 0.85),
    )
    conn.commit()
    rs = conn.execute("SELECT * FROM risk_snapshots WHERE portfolio_id='PF-001'").fetchone()
    check("risk_snapshots INSERT+SELECT", rs is not None)

    # === 7. factor_values ===
    print("\n=== 7. factor_values ===")
    factors = []
    for i in range(50):
        ts = (base_time + timedelta(seconds=i * 3)).isoformat()
        factors.append(("F_MOMENTUM_20D", "600519.SH", ts, 0.75 + i * 0.001, 100))
    conn.executemany(
        """INSERT INTO factor_values (factor_id, symbol, timestamp, value, quality)
        VALUES (?, ?, ?, ?, ?)""",
        factors,
    )

    fv = conn.execute("SELECT COUNT(*) FROM factor_values WHERE factor_id='F_MOMENTUM_20D'").fetchone()[0]
    check("factor_values INSERT 50 rows", fv >= 50, f"got {fv}")

    # === 8. 性能测试 ===
    print("\n=== 8. Performance ===")
    start = time.time()
    large_ticks = []
    for i in range(10000):
        ts = (base_time + timedelta(seconds=i * 3)).isoformat()
        large_ticks.append(
            (
                "600000.SH",
                ts,
                10.0 + i * 0.01,
                1000 + i,
                10000.0 + i * 100,
                9.99 + i * 0.01,
                10.01 + i * 0.01,
                5000 + i,
                6000 + i,
                "perf_test",
                100,
            )
        )
    conn.executemany(
        """INSERT INTO tick_data
        (symbol, timestamp, price, volume, amount, bid1, ask1, bid_vol1, ask_vol1, data_source, quality_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        large_ticks,
    )
    elapsed = time.time() - start
    check("10000 tick INSERT < 20s", elapsed < 20.0, f"took {elapsed:.2f}s")

    start = time.time()
    kline_count = conn.execute("SELECT COUNT(*) FROM kline_3s WHERE symbol='600519.SH'").fetchone()[0]
    elapsed = time.time() - start
    check("kline_3s aggregation < 2s", elapsed < 2.0, f"took {elapsed:.2f}s")

    # === Cleanup ===
    print("\n=== Cleanup ===")
    conn.execute("DELETE FROM orders WHERE order_id='ORD-001'")
    conn.execute("DELETE FROM positions WHERE portfolio_id='PF-001'")
    conn.execute("DELETE FROM backtest_trades WHERE backtest_id='BT-001'")
    conn.execute("DELETE FROM backtest_results WHERE backtest_id='BT-001'")
    conn.execute("DELETE FROM risk_snapshots WHERE portfolio_id='PF-001'")
    conn.execute("DELETE FROM tick_data WHERE data_source='test'")
    conn.execute("DELETE FROM tick_data WHERE data_source='perf_test'")
    conn.execute("DELETE FROM factor_values WHERE factor_id='F_MOMENTUM_20D'")
    conn.commit()
    check("cleanup", True)

    conn.close()

    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")
    if failed > 0:
        sys.exit(1)
    else:
        print("ALL TESTS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    test_all()
