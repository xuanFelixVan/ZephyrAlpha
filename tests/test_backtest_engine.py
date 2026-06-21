# [A_test] module_id: SRC-TST-0408 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain-infra_ops/rollback-system/blueprint.md
# [MODULE] tests.test_backtest_engine
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self

from __future__ import annotations

import math

import pytest

from zephyr.governance.backtest_engine import (
    BacktestEngine,
    BacktestResult,
    ExecutionSim,
    compute_sharpe,
)


class TestBacktestResult:
    def test_instantiation_defaults(self):
        br = BacktestResult()
        assert br.annual_return == 0.0
        assert br.max_drawdown == 0.0
        assert br.sharpe == 0.0
        assert br.calmar == 0.0
        assert br.daily_pnl == []
        assert br.turnover == 0.0
        assert br.benchmark_vs_csi300 == 0.0
        assert br.benchmark_vs_csi500 == 0.0
        assert br.benchmark_vs_treasury == 0.0

    def test_instantiation_with_values(self):
        br = BacktestResult(
            annual_return=0.15,
            max_drawdown=0.08,
            sharpe=1.5,
            calmar=1.875,
            daily_pnl=[100.0, -50.0],
            turnover=2.5,
        )
        assert br.annual_return == 0.15
        assert br.sharpe == 1.5
        assert len(br.daily_pnl) == 2


class TestExecutionSim:
    def test_instantiation_defaults(self):
        sim = ExecutionSim()
        assert sim.slippage_bps == 2.0
        assert sim.commission_bps == 0.03
        assert sim.impact_bps == 1.0

    def test_simulate_buy(self):
        sim = ExecutionSim(slippage_bps=2.0, commission_bps=0.03, impact_bps=1.0)
        total_bps = 2.0 + 0.03 + 1.0
        notional = 10000.0
        result = sim.simulate(notional, side="BUY")
        expected = notional * (1.0 - total_bps / 10000.0)
        assert abs(result - expected) < 1e-10

    def test_simulate_sell(self):
        sim = ExecutionSim(slippage_bps=2.0, commission_bps=0.03, impact_bps=1.0)
        total_bps = 2.0 + 0.03 + 1.0
        notional = 10000.0
        result = sim.simulate(notional, side="SELL")
        expected = notional * (1.0 + total_bps / 10000.0)
        assert abs(result - expected) < 1e-10

    def test_simulate_zero_notional(self):
        sim = ExecutionSim()
        result = sim.simulate(0.0, side="BUY")
        assert result == 0.0

    def test_simulate_custom_bps(self):
        sim = ExecutionSim(slippage_bps=10.0, commission_bps=5.0, impact_bps=5.0)
        notional = 100000.0
        result_buy = sim.simulate(notional, side="BUY")
        expected_buy = notional * (1.0 - 20.0 / 10000.0)
        assert abs(result_buy - expected_buy) < 1e-10

    def test_simulate_large_notional(self):
        sim = ExecutionSim()
        result = sim.simulate(1e9, side="BUY")
        assert result < 1e9
        assert result > 0


class TestBacktestEngineInstantiation:
    def test_instantiation(self):
        engine = BacktestEngine()
        assert engine.exec_sim is not None
        assert isinstance(engine.exec_sim, ExecutionSim)


class TestBacktestEngineRun:
    def test_run_returns_backtest_result(self):
        engine = BacktestEngine()
        signals = [{"action": "BUY"}]
        prices = [100.0]
        result = engine.run(signals, prices)
        assert isinstance(result, BacktestResult)

    def test_run_daily_pnl_length_matches_min(self):
        engine = BacktestEngine()
        signals = [{"action": "BUY"}] * 5
        prices = [100.0, 101.0, 102.0, 103.0, 104.0]
        result = engine.run(signals, prices)
        assert len(result.daily_pnl) == 5

    def test_run_unequal_lengths_uses_min(self):
        engine = BacktestEngine()
        signals = [{"action": "BUY"}] * 3
        prices = [100.0, 101.0, 102.0, 103.0, 104.0]
        result = engine.run(signals, prices)
        assert len(result.daily_pnl) == 3

    def test_run_empty_signals_and_prices(self):
        engine = BacktestEngine()
        result = engine.run([], [])
        assert isinstance(result, BacktestResult)
        assert len(result.daily_pnl) == 0

    def test_run_empty_signals_with_prices(self):
        engine = BacktestEngine()
        result = engine.run([], [100.0])
        assert len(result.daily_pnl) == 0

    def test_run_signals_with_empty_prices(self):
        engine = BacktestEngine()
        result = engine.run([{"action": "BUY"}], [])
        assert len(result.daily_pnl) == 0


class TestBacktestEngineCompareBenchmarks:
    def test_compare_benchmarks_positive_excess(self):
        engine = BacktestEngine()
        result = engine.compare_benchmarks(0.15)
        assert result["CSI300_excess"] == round(0.15 - 0.08, 4)
        assert result["CSI500_excess"] == round(0.15 - 0.10, 4)
        assert result["TREASURY_excess"] == round(0.15 - 0.03, 4)

    def test_compare_benchmarks_negative_excess(self):
        engine = BacktestEngine()
        result = engine.compare_benchmarks(0.05)
        assert result["CSI300_excess"] == round(0.05 - 0.08, 4)
        assert result["CSI500_excess"] == round(0.05 - 0.10, 4)
        assert result["TREASURY_excess"] == round(0.05 - 0.03, 4)

    def test_compare_benchmarks_zero_return(self):
        engine = BacktestEngine()
        result = engine.compare_benchmarks(0.0)
        assert result["CSI300_excess"] == -0.08
        assert result["CSI500_excess"] == -0.10
        assert result["TREASURY_excess"] == -0.03

    def test_compare_benchmarks_returns_three_keys(self):
        engine = BacktestEngine()
        result = engine.compare_benchmarks(0.12)
        assert len(result) == 3
        assert "CSI300_excess" in result
        assert "CSI500_excess" in result
        assert "TREASURY_excess" in result


class TestComputeSharpe:
    def test_empty_returns_zero(self):
        assert compute_sharpe([]) == 0.0

    def test_single_return(self):
        result = compute_sharpe([0.01])
        assert isinstance(result, float)

    def test_constant_returns_zero(self):
        result = compute_sharpe([0.01, 0.01, 0.01])
        assert result == 0.0

    def test_positive_sharpe(self):
        daily_returns = [0.01, 0.02, -0.005, 0.015, 0.008]
        result = compute_sharpe(daily_returns)
        assert result > 0.0

    def test_negative_sharpe(self):
        daily_returns = [-0.02, -0.01, -0.03, 0.005, -0.015]
        result = compute_sharpe(daily_returns)
        assert result < 0.0

    def test_custom_risk_free(self):
        daily_returns = [0.01, 0.02, 0.015]
        result_default = compute_sharpe(daily_returns, risk_free=0.03)
        result_high = compute_sharpe(daily_returns, risk_free=0.10)
        assert result_high < result_default

    def test_annualization_factor(self):
        daily_returns = [0.01, -0.005, 0.02, 0.0, -0.01, 0.015]
        result = compute_sharpe(daily_returns)
        assert abs(result) > 0
        assert isinstance(result, float)

    def test_two_returns(self):
        result = compute_sharpe([0.01, -0.01])
        assert isinstance(result, float)
        assert result != 0.0
