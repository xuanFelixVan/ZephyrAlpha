# [BLUEPRINT] MOD-SIM-021 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""MOD-SIM-012 Simulation Result Analyzer — 仿真结果分析器单元测试。

覆盖: 单场景指标、多场景聚合(mean/std/分位数/CI)、分布直方图、Jarque-Bera 正态性、
可视化数据、空列表、输入校验、frozen。
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from zephyr.simulation.result_analyzer import (
    AggregateAnalysis,
    AnalysisConfig,
    DistributionAnalysis,
    ScenarioMetrics,
    SimulationAnalysisError,
    SimulationAnalysisReport,
    SimulationResultAnalyzer,
)
from zephyr.simulation.strategy_simulator import (
    Action,
    EquityPoint,
    Signal,
    SignalContext,
    SimulationResult,
    StrategySimulator,
    StrategySpec,
)


def make_result(equities: list[float], trades: int = 0) -> SimulationResult:
    """构建 SimulationResult (equity_curve 由 equities 列表生成)。"""
    initial = equities[0] if equities else 1_000_000.0
    curve = [EquityPoint(timestamp=i, equity=e, cash=e, positions_value=0.0) for i, e in enumerate(equities)]
    final = equities[-1] if equities else initial
    return SimulationResult(
        equity_curve=curve,
        trade_log=[],
        signal_log=[],
        initial_capital=initial,
        final_equity=final,
        total_return=(final - initial) / initial,
        trades_count=trades,
        bars_simulated=max(0, len(equities) - 1),
    )


def make_results(n: int, base: float = 1_000_000.0) -> list[SimulationResult]:
    """构建 n 个仿真结果(净值线性上升 10%)。"""
    results = []
    for i in range(n):
        eq = [base, base * 1.02, base * 1.05, base * 1.10]
        results.append(make_result(eq, trades=i + 1))
    return results


# ──────────────────────────────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────────────────────────────


class TestConfig:
    def test_default(self):
        cfg = AnalysisConfig()
        assert cfg.confidence_level == 0.95
        assert cfg.annualization_factor == 252
        assert cfg.histogram_bins == 10

    def test_invalid_confidence(self):
        with pytest.raises(SimulationAnalysisError):
            AnalysisConfig(confidence_level=0.0)
        with pytest.raises(SimulationAnalysisError):
            AnalysisConfig(confidence_level=1.0)

    def test_invalid_annualization(self):
        with pytest.raises(SimulationAnalysisError):
            AnalysisConfig(annualization_factor=0)

    def test_frozen(self):
        cfg = AnalysisConfig()
        with pytest.raises(Exception):
            cfg.confidence_level = 0.99  # type: ignore[misc]


# ──────────────────────────────────────────────────────────────────────────────
# 输入校验
# ──────────────────────────────────────────────────────────────────────────────


class TestInputValidation:
    def test_non_list(self):
        analyzer = SimulationResultAnalyzer()
        with pytest.raises(SimulationAnalysisError):
            analyzer.analyze("not a list")  # type: ignore[arg-type]

    def test_non_simulation_result_element(self):
        analyzer = SimulationResultAnalyzer()
        with pytest.raises(SimulationAnalysisError):
            analyzer.analyze([make_result([100.0, 110.0]), "not a result"])  # type: ignore[list-item]

    def test_analyze_single_non_result(self):
        analyzer = SimulationResultAnalyzer()
        with pytest.raises(SimulationAnalysisError):
            analyzer.analyze_single({"bad": 1})  # type: ignore[arg-type]

    def test_error_code(self):
        assert SimulationAnalysisError.error_code == "ZA-SIM-0012"


# ──────────────────────────────────────────────────────────────────────────────
# 单场景指标
# ──────────────────────────────────────────────────────────────────────────────


class TestScenarioMetrics:
    def test_total_return(self):
        analyzer = SimulationResultAnalyzer()
        r = make_result([1_000_000.0, 1_100_000.0])
        sm = analyzer.analyze_single(r)
        assert sm.total_return == pytest.approx(0.10)

    def test_max_drawdown_negative(self):
        analyzer = SimulationResultAnalyzer()
        # 1M → 1.2M → 0.9M → 1.1M: 最大回撤从 1.2M 到 0.9M
        r = make_result([1_000_000.0, 1_200_000.0, 900_000.0, 1_100_000.0])
        sm = analyzer.analyze_single(r)
        assert sm.max_drawdown < 0
        # (0.9M - 1.2M)/1.2M = -0.25
        assert sm.max_drawdown == pytest.approx(-0.25, rel=1e-2)

    def test_volatility_zero_for_flat(self):
        analyzer = SimulationResultAnalyzer()
        r = make_result([100.0, 100.0, 100.0, 100.0])
        sm = analyzer.analyze_single(r)
        assert sm.volatility == 0.0
        assert sm.sharpe == 0.0

    def test_win_rate(self):
        analyzer = SimulationResultAnalyzer()
        # 4 个权益点 → 3 个收益: +, +, +
        r = make_result([100.0, 101.0, 102.0, 103.0])
        sm = analyzer.analyze_single(r)
        assert sm.win_rate == pytest.approx(1.0)

    def test_win_rate_mixed(self):
        analyzer = SimulationResultAnalyzer()
        # 收益: +, -, + → 胜率 2/3
        r = make_result([100.0, 101.0, 100.5, 102.0])
        sm = analyzer.analyze_single(r)
        assert sm.win_rate == pytest.approx(2.0 / 3.0)

    def test_single_equity_point(self):
        """单点 equity_curve → 退化指标。"""
        analyzer = SimulationResultAnalyzer()
        r = make_result([100.0])
        sm = analyzer.analyze_single(r)
        assert sm.volatility == 0.0
        assert sm.sharpe == 0.0

    def test_trades_count(self):
        analyzer = SimulationResultAnalyzer()
        r = make_result([100.0, 110.0], trades=5)
        sm = analyzer.analyze_single(r)
        assert sm.trades_count == 5


# ──────────────────────────────────────────────────────────────────────────────
# 跨场景聚合
# ──────────────────────────────────────────────────────────────────────────────


class TestAggregation:
    def test_empty_list(self):
        analyzer = SimulationResultAnalyzer()
        report = analyzer.analyze([])
        assert report.aggregate.scenario_count == 0
        assert report.aggregate.metrics == {}
        assert "无仿真结果" in report.summary

    def test_scenario_count(self):
        analyzer = SimulationResultAnalyzer()
        report = analyzer.analyze(make_results(5))
        assert report.aggregate.scenario_count == 5

    def test_mean_total_return(self):
        analyzer = SimulationResultAnalyzer()
        report = analyzer.analyze(make_results(3))
        tr = report.aggregate.metrics["total_return"]
        # 每个场景 total_return = 0.10
        assert tr.mean == pytest.approx(0.10)
        assert tr.std == pytest.approx(0.0, abs=1e-9)

    def test_percentiles(self):
        analyzer = SimulationResultAnalyzer()
        # 3 个场景, trades_count = 1, 2, 3
        report = analyzer.analyze(make_results(3))
        tc = report.aggregate.metrics["trades_count"]
        assert tc.min == 1
        assert tc.max == 3
        assert tc.p50 == pytest.approx(2.0)

    def test_confidence_interval_single_scenario_is_none(self):
        analyzer = SimulationResultAnalyzer()
        report = analyzer.analyze(make_results(1))
        tr = report.aggregate.metrics["total_return"]
        assert tr.ci_lower is None
        assert tr.ci_upper is None

    def test_confidence_interval_multiple(self):
        analyzer = SimulationResultAnalyzer()
        # 不同收益的场景
        r1 = make_result([100.0, 110.0])  # +10%
        r2 = make_result([100.0, 120.0])  # +20%
        report = analyzer.analyze([r1, r2])
        tr = report.aggregate.metrics["total_return"]
        assert tr.ci_lower is not None
        assert tr.ci_upper is not None
        assert tr.ci_lower < tr.mean < tr.ci_upper

    def test_std_zero_returns_ci_equal_mean(self):
        analyzer = SimulationResultAnalyzer()
        # 两个相同收益场景 → std=0 → CI = mean
        r1 = make_result([100.0, 110.0])
        r2 = make_result([100.0, 110.0])
        report = analyzer.analyze([r1, r2])
        tr = report.aggregate.metrics["total_return"]
        assert tr.ci_lower == pytest.approx(tr.mean)
        assert tr.ci_upper == pytest.approx(tr.mean)

    def test_all_metrics_present(self):
        analyzer = SimulationResultAnalyzer()
        report = analyzer.analyze(make_results(3))
        for name in [
            "total_return",
            "annualized_return",
            "volatility",
            "sharpe",
            "max_drawdown",
            "win_rate",
            "trades_count",
        ]:
            assert name in report.aggregate.metrics


# ──────────────────────────────────────────────────────────────────────────────
# 分布分析
# ──────────────────────────────────────────────────────────────────────────────


class TestDistribution:
    def test_histogram_bins_and_counts(self):
        analyzer = SimulationResultAnalyzer(AnalysisConfig(histogram_bins=5))
        report = analyzer.analyze(make_results(3))
        dist = report.distribution
        assert len(dist.histogram_bins) == 6  # n_bins+1 edges
        assert len(dist.histogram_counts) == 5
        assert sum(dist.histogram_counts) == dist.total_returns

    def test_insufficient_returns_is_normal(self):
        """样本不足(<3) → 默认正态(不拒绝)。"""
        analyzer = SimulationResultAnalyzer()
        r = make_result([100.0, 101.0])  # 1 个收益
        report = analyzer.analyze([r])
        assert report.distribution.total_returns < 3
        assert report.distribution.is_normal is True

    def test_jarque_bera_normal_for_symmetric(self):
        """对称正态样本 → JB 低 → 不拒绝正态。"""
        analyzer = SimulationResultAnalyzer()
        rng = np.random.default_rng(42)
        # 构建净值序列使其收益近似正态
        eq = [1_000_000.0]
        for _ in range(500):
            eq.append(eq[-1] * (1 + rng.standard_normal() * 0.01))
        r = make_result(eq)
        report = analyzer.analyze([r])
        # 大量正态样本 → 不拒绝正态
        assert report.distribution.is_normal is True

    def test_jarque_bera_rejects_skewed(self):
        """强偏样本 → JB 高 → 拒绝正态。"""
        analyzer = SimulationResultAnalyzer()
        rng = np.random.default_rng(1)
        # 强右偏: 大量小负收益 + 偶尔大涨
        eq = [1_000_000.0]
        for _ in range(500):
            shock = 0.05 if rng.random() < 0.05 else -0.005
            eq.append(eq[-1] * (1 + shock))
        r = make_result(eq)
        report = analyzer.analyze([r])
        assert report.distribution.is_normal is False
        assert report.distribution.jarque_bera_stat > 5.99


# ──────────────────────────────────────────────────────────────────────────────
# 可视化 + 报告
# ──────────────────────────────────────────────────────────────────────────────


class TestVisualizationAndReport:
    def test_equity_curve_ensemble(self):
        analyzer = SimulationResultAnalyzer()
        report = analyzer.analyze(make_results(3))
        assert len(report.visualization.equity_curve_ensemble) == 3
        # 每条曲线有 4 个点
        assert all(len(curve) == 4 for curve in report.visualization.equity_curve_ensemble)

    def test_metric_summary(self):
        analyzer = SimulationResultAnalyzer()
        report = analyzer.analyze(make_results(3))
        assert "total_return" in report.visualization.metric_summary
        assert report.visualization.metric_summary["total_return"] == pytest.approx(0.10)

    def test_summary_contains_key_info(self):
        analyzer = SimulationResultAnalyzer()
        report = analyzer.analyze(make_results(5))
        s = report.summary
        assert "5" in s
        assert "置信区间" in s
        assert "Sharpe" in s

    def test_report_is_frozen(self):
        analyzer = SimulationResultAnalyzer()
        report = analyzer.analyze(make_results(2))
        with pytest.raises(Exception):
            report.summary = "x"  # type: ignore[misc]

    def test_integration_with_strategy_simulator(self):
        """端到端: 用 StrategySimulator 生成结果 → 分析。"""
        from zephyr.simulation.scenario_generator import (
            MonteCarloParams,
            ScenarioGenerator,
        )

        gen = ScenarioGenerator()
        sim = StrategySimulator()

        def momentum(ctx: SignalContext) -> list[Signal]:
            if len(ctx.market_window) < 2:
                return []
            ret = ctx.market_window["close"].pct_change().iloc[-1]
            if ret > 0:
                return [Signal("SIM", Action.BUY, target_weight=1.0)]
            return [Signal("SIM", Action.SELL)]

        results = []
        for seed in range(10):
            sc = gen.generate_monte_carlo(MonteCarloParams(start_price=100.0, n_bars=100, seed=seed))
            r = sim.run(sc.market_data, StrategySpec(signal_fn=momentum))
            results.append(r)

        analyzer = SimulationResultAnalyzer()
        report = analyzer.analyze(results)
        assert report.aggregate.scenario_count == 10
        assert "total_return" in report.aggregate.metrics
        assert report.distribution.total_returns > 0
