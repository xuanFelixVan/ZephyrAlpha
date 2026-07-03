# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.tests.test_event_driven_engine
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.implementations.event_driven_engine; zephyr.backtest.core.tick_replay
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
"""event_driven_engine.py 验证脚本（TTL=task_bound，施工完成后退役）"""
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
        # 生成20个 Tick（20秒），价格从10.0涨到10.5再回落到10.2（模拟冲高回落）
        base_time = datetime(2024, 1, 15, 9, 30, 0)
        rows = []
        for i in range(20):
            ts = base_time.replace(second=i)
            if i < 10:
                price = 10.0 + i * 0.05  # 涨到10.5
            else:
                price = 10.5 - (i - 10) * 0.03  # 回落到10.2
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


def main() -> None:
    print("=== Test 1: EventDrivenEngine Tick 级回测 ===")
    config = BacktestConfig(initial_capital=Decimal("100000"))
    engine = EventDrivenEngine(config=config)

    # 做T策略：前5秒买入，第15秒卖出
    call_count = [0]

    def strategy(tick_event: TickEvent) -> dict[str, float]:
        call_count[0] += 1
        seq = tick_event.sequence
        # 前5秒建仓50%
        if seq < 5:
            return {"600000.SH": 0.5}
        # 第15秒清仓
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

    print(f"  strategy_id: {result.strategy_id}")
    print(f"  total_return: {result.total_return:.4f}")
    print(f"  annual_return: {result.annual_return:.4f}")
    print(f"  sharpe_ratio: {result.sharpe_ratio}")
    print(f"  max_drawdown: {result.max_drawdown:.4f}")
    print(f"  trades_count: {result.trades_count}")
    print(f"  win_rate: {result.win_rate}")
    print(f"  overfitting_flag: {result.overfitting_flag}")
    print(f"  idempotency_key: {result.idempotency_key}")
    print(f"  strategy回调次数: {call_count[0]}")

    # 验证 BacktestResult 11必填字段（CTR-P1-016）
    required_fields = [
        "annual_return", "end_date", "idempotency_key", "max_drawdown",
        "sharpe_ratio", "start_date", "strategy_id", "timestamp",
        "total_return", "trades_count", "win_rate",
    ]
    for f in required_fields:
        val = getattr(result, f)
        assert val is not None, f"BacktestResult 必填字段 {f} 为 None"
    print("  PASS: BacktestResult 11必填字段全部填充")

    # 验证策略ID
    assert result.strategy_id == "test_make_T"
    # 验证是 BacktestResult 实例
    assert isinstance(result, BacktestResult)
    print("  PASS: EventDrivenEngine Tick 级回测")

    print()
    print("=== Test 2: run() 向量化模式应拒绝 ===")
    try:
        engine.run(signals=[], prices=[])
        print("  FAIL: 应该抛出 EventDrivenEngineError")
        return
    except EventDrivenEngineError as e:
        print(f"  正确拒绝: {e}")
    print("  PASS: run() 向量化模式拒绝")

    print()
    print("=== Test 3: 多次回测结果累积 ===")
    # 再跑一次
    result2 = engine.run_tick(
        provider=MockTickProvider(),
        symbols=["600000.SH"],
        start=datetime(2024, 1, 15),
        end=datetime(2024, 1, 15),
        strategy_callback=lambda e: {"600000.SH": 0.3} if e.sequence < 3 else {},
        strategy_name="test_2",
    )
    assert len(engine.results) == 2, f"expected 2 results, got {len(engine.results)}"
    assert result2.strategy_id == "test_2"
    print(f"  累积结果数: {len(engine.results)}")
    print("  PASS: 多次回测结果累积")

    print()
    print("ALL OK")


if __name__ == "__main__":
    main()
