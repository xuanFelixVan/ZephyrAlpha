# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.test_event_driven_engine
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [TTL] permanent
"""event_driven_engine 正式测试（原 scripts/tests/ 临时验证脚本转正）"""
from datetime import datetime
from decimal import Decimal

import pandas as pd

from zephyr.backtest.implementations.event_driven_engine import (
    EventDrivenEngine,
    EventDrivenEngineError,
)
from zephyr.backtest.implementations.vectorized_engine import BacktestConfig
from zephyr.backtest.core.tick_replay import TickEvent, TickReplayConfig
from zephyr.backtest.core.engine_base import BacktestResult


class MockTickProvider:
    """模拟 MiniQmtProvider"""

    def fetch_historical(self, symbol, start, end, interval="tick"):
        base_time = datetime(2024, 1, 15, 9, 30, 0)
        rows = []
        for i in range(20):
            ts = base_time.replace(second=i)
            if i < 10:
                price = 10.0 + i * 0.05
            else:
                price = 10.5 - (i - 10) * 0.03
            row = {
                "timestamp": ts, "last_price": price, "open": 10.0,
                "high": price + 0.02, "low": price - 0.02,
                "prev_close": 9.99, "amount": Decimal("1000000"),
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


def test_event_driven_tick_backtest():
    """EventDrivenEngine Tick 级回测"""
    config = BacktestConfig(initial_capital=Decimal("100000"))
    engine = EventDrivenEngine(config=config)

    def strategy(tick_event: TickEvent) -> dict[str, float]:
        seq = tick_event.sequence
        if seq < 5:
            return {"600000.SH": 0.5}
        elif seq >= 15:
            return {"600000.SH": 0.0}
        return {}

    result = engine.run_tick(
        provider=MockTickProvider(),
        symbols=["600000.SH"],
        start=datetime(2024, 1, 15),
        end=datetime(2024, 1, 15),
        strategy_callback=strategy,
        tick_config=TickReplayConfig(speed="max_speed"),
        strategy_name="test_make_T",
    )

    required_fields = [
        "annual_return", "end_date", "idempotency_key", "max_drawdown",
        "sharpe_ratio", "start_date", "strategy_id", "timestamp",
        "total_return", "trades_count", "win_rate",
    ]
    for f in required_fields:
        val = getattr(result, f)
        assert val is not None, f"BacktestResult 必填字段 {f} 为 None"
    assert result.strategy_id == "test_make_T"
    assert isinstance(result, BacktestResult)


def test_run_vectorized_mode_rejected():
    """run() 向量化模式应拒绝"""
    config = BacktestConfig(initial_capital=Decimal("100000"))
    engine = EventDrivenEngine(config=config)
    try:
        engine.run(signals=[], prices=[])
        assert False, "应该抛出 EventDrivenEngineError"
    except EventDrivenEngineError:
        pass


def test_multiple_backtests_accumulate():
    """多次回测结果累积"""
    config = BacktestConfig(initial_capital=Decimal("100000"))
    engine = EventDrivenEngine(config=config)
    engine.run_tick(
        provider=MockTickProvider(),
        symbols=["600000.SH"],
        start=datetime(2024, 1, 15),
        end=datetime(2024, 1, 15),
        strategy_callback=strategy_callback_simple,
        strategy_name="test_1",
    )
    result2 = engine.run_tick(
        provider=MockTickProvider(),
        symbols=["600000.SH"],
        start=datetime(2024, 1, 15),
        end=datetime(2024, 1, 15),
        strategy_callback=strategy_callback_simple,
        strategy_name="test_2",
    )
    assert len(engine.results) == 2, f"expected 2 results, got {len(engine.results)}"
    assert result2.strategy_id == "test_2"


def strategy_callback_simple(tick_event: TickEvent) -> dict[str, float]:
    """简单策略回调"""
    if tick_event.sequence < 3:
        return {"600000.SH": 0.3}
    return {}
