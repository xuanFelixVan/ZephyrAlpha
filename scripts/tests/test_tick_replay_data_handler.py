# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.tests.test_tick_replay_data_handler
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.tick_replay; zephyr.backtest.core.data_handler
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] TTL=task_bound（施工完成后退役）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] task_bound
"""tick_replay.py + data_handler.py 验证脚本（TTL=task_bound，施工完成后退役）"""
from datetime import datetime
from decimal import Decimal

import pandas as pd

from zephyr.backtest.core.tick_replay import (
    TickReplayEngine,
    TickReplayConfig,
    TickEvent,
)
from zephyr.backtest.core.data_handler import (
    BacktestDataHandler,
    MultiSourceDataHandler,
    DataHandlerError,
)
from zephyr.backtest.core.matching_logic import TickSnapshot


class MockTickProvider:
    """模拟 MiniQmtProvider（避免依赖 xtquant）"""

    def fetch_historical(self, symbol, start, end, interval="tick"):
        # 生成10个 Tick 的模拟数据
        base_time = datetime(2024, 1, 15, 9, 30, 0)
        rows = []
        for i in range(10):
            ts = base_time.replace(second=i)
            price = 10.50 + i * 0.01
            row = {
                "timestamp": ts,
                "last_price": price,
                "open": 10.50,
                "high": price + 0.02,
                "low": price - 0.02,
                "prev_close": 10.49,
                "amount": Decimal("1000000"),
                "volume": Decimal("10000"),
                "pvolume": 0,
                "stock_status": 0,
                "open_interest": 0,
                "last_settlement": Decimal("0"),
                "settlement_price": Decimal("0"),
                "transaction_num": 100,
                "ask_price_1": price, "ask_price_2": price + 0.01,
                "ask_price_3": price + 0.02, "ask_price_4": price + 0.03,
                "ask_price_5": price + 0.04,
                "bid_price_1": price - 0.01, "bid_price_2": price - 0.02,
                "bid_price_3": price - 0.03, "bid_price_4": price - 0.04,
                "bid_price_5": price - 0.05,
                "ask_vol_1": 100, "ask_vol_2": 200, "ask_vol_3": 300,
                "ask_vol_4": 400, "ask_vol_5": 500,
                "bid_vol_1": 100, "bid_vol_2": 200, "bid_vol_3": 300,
                "bid_vol_4": 400, "bid_vol_5": 500,
                "symbol": symbol,
            }
            rows.append(row)
        return pd.DataFrame(rows)


def main() -> None:
    print("=== Test 1: TickReplayEngine 基本回放 ===")
    provider = MockTickProvider()
    engine = TickReplayEngine(
        provider=provider,
        symbols=["600000.SH"],
        start=datetime(2024, 1, 15),
        end=datetime(2024, 1, 15),
        config=TickReplayConfig(speed="max_speed"),
    )

    events = []

    def on_tick(event: TickEvent) -> None:
        events.append(event)
        if len(events) <= 3:  # 只打印前3个
            print(
                f"  seq={event.sequence} ts={event.timestamp} sym={event.symbol} "
                f"price={event.tick_data.last_price} ask1={event.tick_data.ask_price[0]}"
            )

    engine.run(callback=on_tick)
    stats = engine.get_statistics()
    print(f"  总计: {stats.total_ticks} ticks, 耗时 {stats.total_duration_s:.3f}s")
    assert stats.total_ticks == 10, f"expected 10 ticks, got {stats.total_ticks}"
    assert stats.symbols == ["600000.SH"]
    # 验证按时间戳排序
    timestamps = [e.timestamp for e in events]
    assert timestamps == sorted(timestamps), "Tick 必须按时间戳排序"
    print("  PASS: TickReplayEngine 基本回放")

    print()
    print("=== Test 2: TickReplayEngine 时间窗口过滤 ===")
    engine2 = TickReplayEngine(
        provider=provider,
        symbols=["600000.SH"],
        start=datetime(2024, 1, 15),
        end=datetime(2024, 1, 15),
        config=TickReplayConfig(speed="max_speed", time_window=("09:30:00", "09:30:05")),
    )
    events2 = []
    engine2.run(callback=lambda e: events2.append(e))
    print(f"  时间窗口 09:30:00-09:30:05 内 ticks: {len(events2)}")
    assert len(events2) == 6, f"expected 6 ticks in window, got {len(events2)}"
    print("  PASS: 时间窗口过滤")

    print()
    print("=== Test 3: TickReplayEngine 多标的同步 ===")
    engine3 = TickReplayEngine(
        provider=provider,
        symbols=["600000.SH", "000001.SZ"],
        start=datetime(2024, 1, 15),
        end=datetime(2024, 1, 15),
        config=TickReplayConfig(speed="max_speed"),
    )
    events3 = []
    engine3.run(callback=lambda e: events3.append(e))
    syms_seen = {e.symbol for e in events3}
    print(f"  总 ticks: {len(events3)}, symbols: {syms_seen}")
    assert len(events3) == 20, f"expected 20 ticks (10x2), got {len(events3)}"
    assert syms_seen == {"600000.SH", "000001.SZ"}
    print("  PASS: 多标的同步")

    print()
    print("=== Test 4: TickReplayEngine 5秒K线聚合 ===")
    # 生成5+秒数据
    class MockProvider5s:
        def fetch_historical(self, symbol, start, end, interval="tick"):
            base_time = datetime(2024, 1, 15, 9, 30, 0)
            rows = []
            for i in range(8):
                ts = base_time.replace(second=i)
                price = 10.50 + i * 0.01
                row = {
                    "timestamp": ts, "last_price": price, "open": 10.50,
                    "high": price + 0.02, "low": price - 0.02,
                    "prev_close": 10.49, "amount": Decimal("1000000"),
                    "volume": Decimal("10000"), "pvolume": 0,
                    "stock_status": 0, "open_interest": 0,
                    "last_settlement": Decimal("0"), "settlement_price": Decimal("0"),
                    "transaction_num": 100,
                    "ask_price_1": price, "ask_price_2": price + 0.01,
                    "ask_price_3": price + 0.02, "ask_price_4": price + 0.03,
                    "ask_price_5": price + 0.04,
                    "bid_price_1": price - 0.01, "bid_price_2": price - 0.02,
                    "bid_price_3": price - 0.03, "bid_price_4": price - 0.04,
                    "bid_price_5": price - 0.05,
                    "ask_vol_1": 100, "ask_vol_2": 200, "ask_vol_3": 300,
                    "ask_vol_4": 400, "ask_vol_5": 500,
                    "bid_vol_1": 100, "bid_vol_2": 200, "bid_vol_3": 300,
                    "bid_vol_4": 400, "bid_vol_5": 500,
                    "symbol": symbol,
                }
                rows.append(row)
            return pd.DataFrame(rows)

    engine4 = TickReplayEngine(
        provider=MockProvider5s(),
        symbols=["600000.SH"],
        start=datetime(2024, 1, 15),
        end=datetime(2024, 1, 15),
        config=TickReplayConfig(speed="max_speed", aggregate_5s=True),
    )
    events4 = []
    agg_events = []
    def on_tick_agg(e: TickEvent) -> None:
        events4.append(e)
        if e.sequence == -1:
            agg_events.append(e)

    engine4.run(callback=on_tick_agg)
    print(f"  总 ticks: {len(events4)}, 聚合K线: {len(agg_events)}")
    # 8个Tick跨越8秒，应产生1个5秒聚合K线（第5秒时）
    assert len(agg_events) >= 1, f"expected >=1 agg bar, got {len(agg_events)}"
    if agg_events:
        agg = agg_events[0]
        print(
            f"  聚合K线: open={agg.tick_data.open} high={agg.tick_data.high} "
            f"low={agg.tick_data.low} close={agg.tick_data.last_price}"
        )
    print("  PASS: 5秒K线聚合")

    print()
    print("=== Test 5: MultiSourceDataHandler Tick 模式 ===")
    handler = MultiSourceDataHandler(
        symbols=["600000.SH"],
        start=datetime(2024, 1, 15),
        end=datetime(2024, 1, 15),
        mode="tick",
        tick_provider=MockTickProvider(),
    )
    assert handler.active_source == "tick"
    assert handler.total_ticks == 10
    count = 0
    while True:
        tick_df = handler.next_tick()
        if tick_df is None:
            break
        count += 1
        if count <= 2:
            print(f"  tick {count}: {tick_df.iloc[0]['timestamp']} price={tick_df.iloc[0]['last_price']}")
    print(f"  总计推送: {count} ticks")
    assert count == 10
    print("  PASS: MultiSourceDataHandler Tick 模式")

    print()
    print("=== Test 6: MultiSourceDataHandler batch 模式（DataFrame）===")
    # 构造日线 DataFrame
    dates = pd.date_range("2024-01-01", periods=5, freq="D")
    batch_df = pd.DataFrame({
        "date": dates,
        "symbol": ["600000.SH"] * 5,
        "open": [10.0, 10.1, 10.2, 10.3, 10.4],
        "high": [10.5, 10.6, 10.7, 10.8, 10.9],
        "low": [9.9, 10.0, 10.1, 10.2, 10.3],
        "close": [10.2, 10.3, 10.4, 10.5, 10.6],
        "volume": [100000] * 5,
        "amount": [1000000] * 5,
    })
    handler2 = MultiSourceDataHandler(
        symbols=["600000.SH"],
        start=datetime(2024, 1, 1),
        end=datetime(2024, 1, 5),
        mode="batch",
        batch_data=batch_df,
    )
    assert handler2.active_source == "batch"
    assert handler2.total_bars == 5
    bar_count = 0
    while True:
        bar = handler2.next_bar()
        if bar is None:
            break
        bar_count += 1
    print(f"  总计推送: {bar_count} bars")
    assert bar_count == 5
    print("  PASS: MultiSourceDataHandler batch 模式")

    print()
    print("=== Test 7: MultiSourceDataHandler get_history (PIT) ===")
    handler3 = MultiSourceDataHandler(
        symbols=["600000.SH"],
        start=datetime(2024, 1, 1),
        end=datetime(2024, 1, 5),
        mode="batch",
        batch_data=batch_df,
    )
    # 推送3个bar
    handler3.next_bar()
    handler3.next_bar()
    handler3.next_bar()
    # 获取历史2条（含当前）
    history = handler3.get_history(lookback=2)
    print(f"  get_history(2) 返回 {len(history)} 行")
    assert len(history) == 2
    print("  PASS: get_history PIT")

    print()
    print("ALL OK")


if __name__ == "__main__":
    main()
