# [BLUEPRINT] MOD-SIM-021 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""MOD-SIM-002 Strategy Simulator — 策略仿真器单元测试。

覆盖: 配置校验、单/多标的仿真、PIT无前瞻、做空截断、佣金/滑点、空/单bar、
HOLD不交易、买卖权益、输入校验、signal_log/trade_log 完整性。
"""
from __future__ import annotations

import pandas as pd
import pytest

from zephyr.simulation.strategy_simulator import (
    Action,
    EquityPoint,
    Signal,
    SignalContext,
    SimulatedTrade,
    SimulationResult,
    StrategySimulationError,
    StrategySimulator,
    StrategySimulatorConfig,
    StrategySpec,
)


def make_ohlcv(prices: list[float], symbol: str | None = None) -> pd.DataFrame:
    """构建单标的 OHLCV DataFrame (date-indexed)。

    close=prices, open/high/low 围绕 close, volume=1000。
    """
    dates = pd.date_range("2026-01-01", periods=len(prices), freq="D")
    df = pd.DataFrame({
        "open": prices,
        "high": [p * 1.01 for p in prices],
        "low": [p * 0.99 for p in prices],
        "close": prices,
        "volume": [1000] * len(prices),
    }, index=dates)
    if symbol is not None:
        df = pd.concat({symbol: df}, names=["symbol", "date"])
    return df


def make_multi_ohlcv(symbols: list[str], prices_by_sym: dict[str, list[float]]) -> pd.DataFrame:
    """构建多标的 MultiIndex [symbol, date] OHLCV。"""
    frames = []
    for sym in symbols:
        frames.append(make_ohlcv(prices_by_sym[sym], symbol=sym))
    return pd.concat(frames)


# ──────────────────────────────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────────────────────────────


class TestConfig:
    def test_default_config(self):
        cfg = StrategySimulatorConfig()
        assert cfg.initial_capital == 1_000_000.0
        assert cfg.commission_rate == 0.0003
        assert cfg.min_commission == 5.0
        assert cfg.slippage == 0.001
        assert cfg.allow_short is False

    def test_invalid_initial_capital(self):
        with pytest.raises(StrategySimulationError):
            StrategySimulatorConfig(initial_capital=0)
        with pytest.raises(StrategySimulationError):
            StrategySimulatorConfig(initial_capital=-100)

    def test_invalid_commission_rate(self):
        with pytest.raises(StrategySimulationError):
            StrategySimulatorConfig(commission_rate=-0.001)

    def test_invalid_slippage(self):
        with pytest.raises(StrategySimulationError):
            StrategySimulatorConfig(slippage=-0.01)

    def test_config_is_frozen(self):
        cfg = StrategySimulatorConfig()
        with pytest.raises(Exception):
            cfg.initial_capital = 2000000  # type: ignore[misc]


# ──────────────────────────────────────────────────────────────────────────────
# 输入校验
# ──────────────────────────────────────────────────────────────────────────────


class TestInputValidation:
    def test_non_dataframe(self):
        sim = StrategySimulator()
        with pytest.raises(StrategySimulationError):
            sim.run([1, 2, 3], StrategySpec(signal_fn=lambda ctx: []))

    def test_missing_columns(self):
        sim = StrategySimulator()
        df = pd.DataFrame({"open": [1, 2, 3]}, index=pd.date_range("2026-01-01", periods=3))
        with pytest.raises(StrategySimulationError):
            sim.run(df, StrategySpec(signal_fn=lambda ctx: []))

    def test_signal_fn_not_callable(self):
        sim = StrategySimulator()
        df = make_ohlcv([10, 11, 12])
        with pytest.raises(StrategySimulationError):
            sim.run(df, StrategySpec(signal_fn="not callable"))  # type: ignore[arg-type]

    def test_error_code(self):
        assert StrategySimulationError.error_code == "ZA-SIM-0002"


# ──────────────────────────────────────────────────────────────────────────────
# 仿真核心
# ──────────────────────────────────────────────────────────────────────────────


class TestSimulation:
    def test_empty_dataframe_returns_initial_capital(self):
        sim = StrategySimulator()
        df = pd.DataFrame(columns=["open", "close", "high", "low", "volume"])
        result = sim.run(df, StrategySpec(signal_fn=lambda ctx: []))
        assert result.final_equity == 1_000_000.0
        assert result.total_return == 0.0
        assert result.trades_count == 0

    def test_single_bar_returns_initial_capital(self):
        """单 bar 无法仿真(需 1 bar 历史), 返回初始资金。"""
        sim = StrategySimulator()
        df = make_ohlcv([10.0])
        result = sim.run(df, StrategySpec(signal_fn=lambda ctx: []))
        assert result.final_equity == 1_000_000.0
        assert result.trades_count == 0
        assert result.bars_simulated == 1

    def test_buy_and_hold_profitable(self):
        """买入并持有, 价格上涨 → 盈利。"""
        sim = StrategySimulator(StrategySimulatorConfig(initial_capital=10000.0))

        def buy_first(ctx: SignalContext) -> list[Signal]:
            if ctx.bar_index == 1:
                return [Signal("_default", Action.BUY, target_weight=1.0)]
            return []

        df = make_ohlcv([10.0, 10.0, 11.0, 12.0])
        result = sim.run(df, StrategySpec(signal_fn=buy_first))
        assert result.trades_count == 1
        assert result.final_equity > 10000.0
        assert result.total_return > 0
        assert result.is_profitable

    def test_hold_does_not_trade(self):
        sim = StrategySimulator()

        def always_hold(ctx: SignalContext) -> list[Signal]:
            return [Signal("_default", Action.HOLD)]

        df = make_ohlcv([10.0, 11.0, 12.0, 13.0])
        result = sim.run(df, StrategySpec(signal_fn=always_hold))
        assert result.trades_count == 0
        assert result.final_equity == 1_000_000.0  # 全现金

    def test_pit_no_look_ahead(self):
        """signal_fn 只接收 bar i 之前的数据 (market_window 长度 = i)。"""
        seen_windows = []

        def record_window(ctx: SignalContext) -> list[Signal]:
            seen_windows.append(len(ctx.market_window))
            return []

        df = make_ohlcv([10.0, 11.0, 12.0, 13.0, 14.0])
        sim = StrategySimulator()
        sim.run(df, StrategySpec(signal_fn=record_window))
        # bar 1 → window 长度 1; bar 2 → 2; bar 3 → 3; bar 4 → 4
        assert seen_windows == [1, 2, 3, 4]

    def test_sell_truncates_to_holding(self):
        """禁做空时, SELL 超过持仓量被截断到持仓量。"""
        sim = StrategySimulator(StrategySimulatorConfig(initial_capital=10000.0))
        holdings_seen = []

        def buy_then_sell(ctx: SignalContext) -> list[Signal]:
            if ctx.bar_index == 1:
                return [Signal("_default", Action.BUY, target_weight=1.0)]
            if ctx.bar_index == 2:
                holdings_seen.append(dict(ctx.holdings))
                return [Signal("_default", Action.SELL)]
            return []

        df = make_ohlcv([10.0, 10.0, 10.0, 10.0])
        result = sim.run(df, StrategySpec(signal_fn=buy_then_sell))
        # bar2 时应有持仓, SELL 后清仓
        assert holdings_seen[0].get("_default", 0) > 0
        assert result.trades_count == 2  # 1 buy + 1 sell
        # 卖出后基本全现金(扣佣金)
        assert abs(result.final_equity - 10000.0) < 50.0

    def test_commission_and_slippage_applied(self):
        """BUY 执行价 = open*(1+slippage), 佣金 = max(cost*rate, min)。"""
        sim = StrategySimulator(StrategySimulatorConfig(
            initial_capital=10000.0, commission_rate=0.001, min_commission=0.0, slippage=0.01
        ))

        def buy(ctx: SignalContext) -> list[Signal]:
            if ctx.bar_index == 1:
                return [Signal("_default", Action.BUY, target_weight=1.0)]
            return []

        df = make_ohlcv([10.0, 10.0, 10.0])  # open=10 at bar1
        result = sim.run(df, StrategySpec(signal_fn=buy))
        trade = result.trade_log[0]
        # exec_price = 10 * (1+0.01) = 10.1
        assert trade.price == pytest.approx(10.1, rel=1e-6)
        # target_qty = 1.0 * 10000 / 10.1 ≈ 990.099
        # commission = 990.099 * 10.1 * 0.001 ≈ 10.0
        assert trade.commission == pytest.approx(trade.quantity * trade.price * 0.001, rel=1e-4)

    def test_min_commission_floor(self):
        """小单交易佣金不低于 min_commission。"""
        sim = StrategySimulator(StrategySimulatorConfig(
            initial_capital=100.0, commission_rate=0.0001, min_commission=5.0, slippage=0.0
        ))

        def buy(ctx: SignalContext) -> list[Signal]:
            if ctx.bar_index == 1:
                return [Signal("_default", Action.BUY, target_weight=1.0)]
            return []

        df = make_ohlcv([10.0, 10.0, 10.0])
        result = sim.run(df, StrategySpec(signal_fn=buy))
        trade = result.trade_log[0]
        # cost ≈ 100, rate*cost = 0.01 < 5.0 → commission = 5.0
        assert trade.commission == pytest.approx(5.0, rel=1e-6)

    def test_multi_symbol(self):
        """多标的 MultiIndex 仿真。"""
        sim = StrategySimulator(StrategySimulatorConfig(initial_capital=10000.0))
        called = []

        def buy_both(ctx: SignalContext) -> list[Signal]:
            if ctx.bar_index == 1:
                called.append(True)
                return [
                    Signal("AAA", Action.BUY, target_weight=0.5),
                    Signal("BBB", Action.BUY, target_weight=0.5),
                ]
            return []

        df = make_multi_ohlcv(["AAA", "BBB"], {"AAA": [10, 10, 11], "BBB": [20, 20, 22]})
        result = sim.run(df, StrategySpec(signal_fn=buy_both))
        assert called  # signal_fn 被调用
        assert result.trades_count == 2
        assert result.final_equity > 10000.0

    def test_equity_curve_length(self):
        sim = StrategySimulator()
        df = make_ohlcv([10.0, 11.0, 12.0, 13.0, 14.0])
        result = sim.run(df, StrategySpec(signal_fn=lambda ctx: []))
        # 5 bars → 4 equity points (bar 1..4)
        assert len(result.equity_curve) == 4

    def test_signal_log_records_all_signals(self):
        sim = StrategySimulator()

        def two_signals(ctx: SignalContext) -> list[Signal]:
            return [Signal("_default", Action.HOLD), Signal("_default", Action.HOLD)]

        df = make_ohlcv([10.0, 11.0, 12.0])
        result = sim.run(df, StrategySpec(signal_fn=two_signals))
        # 2 bars × 2 signals = 4
        assert len(result.signal_log) == 4

    def test_signal_fn_exception_does_not_crash(self):
        """signal_fn 抛异常时, 仿真继续(记 warning, 当作无信号)。"""
        sim = StrategySimulator()

        def faulty(ctx: SignalContext) -> list[Signal]:
            if ctx.bar_index == 2:
                raise ValueError("strategy bug")
            return []

        df = make_ohlcv([10.0, 11.0, 12.0, 13.0])
        result = sim.run(df, StrategySpec(signal_fn=faulty))
        # 不报错, 正常完成
        assert result.bars_simulated == 3

    def test_result_is_frozen(self):
        sim = StrategySimulator()
        df = make_ohlcv([10.0, 11.0, 12.0])
        result = sim.run(df, StrategySpec(signal_fn=lambda ctx: []))
        with pytest.raises(Exception):
            result.final_equity = 999  # type: ignore[misc]

    def test_no_data_for_symbol_skips_signal(self):
        """某标的在某 bar 无数据时, 该标的的信号被跳过(不报错)。"""
        sim = StrategySimulator(StrategySimulatorConfig(initial_capital=10000.0))

        def buy_missing(ctx: SignalContext) -> list[Signal]:
            return [Signal("MISSING", Action.BUY, target_weight=1.0)]

        # 只有 _default 标的数据, 信号针对 MISSING 标的 → 跳过
        df = make_ohlcv([10.0, 11.0, 12.0])
        result = sim.run(df, StrategySpec(signal_fn=buy_missing))
        assert result.trades_count == 0

    def test_bars_simulated(self):
        sim = StrategySimulator()
        df = make_ohlcv([10.0, 11.0, 12.0, 13.0])
        result = sim.run(df, StrategySpec(signal_fn=lambda ctx: []))
        assert result.bars_simulated == 3  # 4 bars → 3 simulated steps
