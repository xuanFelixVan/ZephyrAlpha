# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.test_tick_replay_data_handler
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [TTL] permanent
"""tick_replay + data_handler 正式测试（原 scripts/tests/ 临时验证脚本转正）"""
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


def test_tick_replay_basic():
    """TickReplayEngine 基本回放"""
    provider = MockTickProvider()
    engine = TickReplayEngine(
        provider=provider,
        symbols=["600000.SH"],
        start=datetime(2024, 1, 15),
        end=datetime(2024, 1, 15),
        config=TickReplayConfig(speed="max_speed"),
    )
    events = []
    engine.run(callback=lambda e: events.append(e))
    stats = engine.get_statistics()
    assert stats.total_ticks == 10, f"expected 10 ticks, got {stats.total_ticks}"
    assert stats.symbols == ["600000.SH"]
    timestamps = [e.timestamp for e in events]
    assert timestamps == sorted(timestamps), "Tick 必须按时间戳排序"


def test_tick_replay_time_window():
    """TickReplayEngine 时间窗口过滤"""
    provider = MockTickProvider()
    engine = TickReplayEngine(
        provider=provider,
        symbols=["600000.SH"],
        start=datetime(2024, 1, 15),
        end=datetime(2024, 1, 15),
        config=TickReplayConfig(speed="max_speed", time_window=("09:30:00", "09:30:05")),
    )
    events = []
    engine.run(callback=lambda e: events.append(e))
    assert len(events) == 6, f"expected 6 ticks in window, got {len(events)}"


def test_tick_replay_multi_symbol():
    """TickReplayEngine 多标的同步"""
    provider = MockTickProvider()
    engine = TickReplayEngine(
        provider=provider,
        symbols=["600000.SH", "000001.SZ"],
        start=datetime(2024, 1, 15),
        end=datetime(2024, 1, 15),
        config=TickReplayConfig(speed="max_speed"),
    )
    events = []
    engine.run(callback=lambda e: events.append(e))
    syms_seen = {e.symbol for e in events}
    assert len(events) == 20, f"expected 20 ticks (10x2), got {len(events)}"
    assert syms_seen == {"600000.SH", "000001.SZ"}


def test_tick_replay_5s_aggregation():
    """TickReplayEngine 5秒K线聚合"""
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

    engine = TickReplayEngine(
        provider=MockProvider5s(),
        symbols=["600000.SH"],
        start=datetime(2024, 1, 15),
        end=datetime(2024, 1, 15),
        config=TickReplayConfig(speed="max_speed", aggregate_5s=True),
    )
    events = []
    agg_events = []
    def on_tick_agg(e: TickEvent) -> None:
        events.append(e)
        if e.sequence == -1:
            agg_events.append(e)
    engine.run(callback=on_tick_agg)
    assert len(agg_events) >= 1, f"expected >=1 agg bar, got {len(agg_events)}"


def test_multi_source_data_handler_tick_mode():
    """MultiSourceDataHandler Tick 模式"""
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
    assert count == 10


def test_multi_source_data_handler_batch_mode():
    """MultiSourceDataHandler batch 模式（DataFrame）"""
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
    handler = MultiSourceDataHandler(
        symbols=["600000.SH"],
        start=datetime(2024, 1, 1),
        end=datetime(2024, 1, 5),
        mode="batch",
        batch_data=batch_df,
    )
    assert handler.active_source == "batch"
    assert handler.total_bars == 5
    bar_count = 0
    while True:
        bar = handler.next_bar()
        if bar is None:
            break
        bar_count += 1
    assert bar_count == 5


def test_multi_source_data_handler_get_history_pit():
    """MultiSourceDataHandler get_history (PIT)"""
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
    handler = MultiSourceDataHandler(
        symbols=["600000.SH"],
        start=datetime(2024, 1, 1),
        end=datetime(2024, 1, 5),
        mode="batch",
        batch_data=batch_df,
    )
    handler.next_bar()
    handler.next_bar()
    handler.next_bar()
    history = handler.get_history(lookback=2)
    assert len(history) == 2
