# [BLUEPRINT] MOD-SIM-003 | docs/03_modules/_domain_simulation/risk_simulator/blueprint.md
# [MODULE] tests.simulation.test_risk_simulator
# [DOMAIN] D_SIMULATION
# [DEPENDENCIES] zephyr.simulation.risk_simulator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SIM-003 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-SIM-003 Risk Simulator 单元测试.

覆盖: 历史VaR/CVaR、参数VaR、蒙特卡洛VaR、回撤模拟、熔断触发、
全量仿真、边界值、配置自定义、frozen不可变、审计摘要、符号约定.
"""

from __future__ import annotations

import math
import random

import pytest

from zephyr.simulation.risk_simulator import (
    CircuitBreakerResult,
    DrawdownResult,
    RiskConfig,
    RiskMethod,
    RiskSimulationResult,
    RiskSimulator,
    SimulationError,
    VaRResult,
)

# ============== 辅助函数 ==============


def gen_returns(n: int = 100, mean: float = 0.001, std: float = 0.02, seed: int = 42) -> list[float]:
    rng = random.Random(seed)
    return [rng.gauss(mean, std) for _ in range(n)]


# ============== 配置 ==============


class TestRiskConfig:
    def test_defaults(self):
        cfg = RiskConfig()
        assert cfg.confidence_levels == (0.95, 0.99)
        assert cfg.mc_paths == 10000
        assert cfg.mc_seed == 42
        assert cfg.periods_per_year == 252

    def test_frozen(self):
        cfg = RiskConfig()
        with pytest.raises(Exception):
            cfg.mc_paths = 5000  # type: ignore[misc]

    def test_custom(self):
        cfg = RiskConfig(
            confidence_levels=(0.90,),
            mc_paths=1000,
            mc_seed=7,
        )
        assert cfg.confidence_levels == (0.90,)
        assert cfg.mc_paths == 1000
        assert cfg.mc_seed == 7


class TestFrozenDataclasses:
    def test_var_result_frozen(self):
        vr = VaRResult(confidence=0.95, var=0.05, cvar=0.07, method=RiskMethod.HISTORICAL)
        with pytest.raises(Exception):
            vr.var = 0.10  # type: ignore[misc]

    def test_drawdown_frozen(self):
        d = DrawdownResult(max_drawdown=-0.1, max_dd_duration=5, recovery_duration=3, current_drawdown=-0.02)
        with pytest.raises(Exception):
            d.max_drawdown = -0.2  # type: ignore[misc]

    def test_circuit_breaker_frozen(self):
        cb = CircuitBreakerResult(triggered=True, trigger_level=-0.1, hit_count=1, worst_drawdown=-0.15)
        with pytest.raises(Exception):
            cb.triggered = False  # type: ignore[misc]

    def test_simulation_result_frozen(self):
        r = RiskSimulationResult()
        with pytest.raises(Exception):
            r.num_obs = 100  # type: ignore[misc]


# ============== 历史 VaR ==============


class TestHistoricalVaR:
    def test_basic_historical_var(self):
        sim = RiskSimulator()
        returns = [-0.05, -0.02, 0.01, 0.03, 0.05]
        results = sim.calculate_var(returns, confidence_levels=[0.95], method=RiskMethod.HISTORICAL)
        assert len(results) == 1
        vr = results[0]
        assert vr.method == RiskMethod.HISTORICAL
        # VaR 为正数(损失)
        assert vr.var > 0

    def test_historical_var_value(self):
        sim = RiskSimulator()
        returns = [-0.05, -0.02, 0.01, 0.03, 0.05]
        results = sim.calculate_var(returns, confidence_levels=[0.80], method=RiskMethod.HISTORICAL)
        vr = results[0]
        # (1-0.80)*5=1.0, idx=1, sorted[1]=-0.02, VaR=0.02
        assert vr.var == pytest.approx(0.02, abs=1e-9)

    def test_cvar_ge_var(self):
        """CVaR 应 >= VaR(预期短缺 >= VaR)。"""
        sim = RiskSimulator()
        returns = gen_returns(200)
        results = sim.calculate_var(returns, method=RiskMethod.HISTORICAL)
        for vr in results:
            assert vr.cvar >= vr.var - 1e-9

    def test_multiple_confidence_levels(self):
        sim = RiskSimulator()
        results = sim.calculate_var(gen_returns(100), method=RiskMethod.HISTORICAL)
        assert len(results) == 2  # 95%, 99%
        # 99% VaR >= 95% VaR
        assert results[1].var >= results[0].var - 1e-9


# ============== 参数 VaR ==============


class TestParametricVaR:
    def test_parametric_var_positive(self):
        sim = RiskSimulator()
        results = sim.calculate_var(gen_returns(100), confidence_levels=[0.95], method=RiskMethod.PARAMETRIC)
        assert results[0].var > 0
        assert results[0].method == RiskMethod.PARAMETRIC

    def test_parametric_var_value(self):
        sim = RiskSimulator()
        returns = gen_returns(200, mean=0.001, std=0.01, seed=1)
        results = sim.calculate_var(returns, confidence_levels=[0.95], method=RiskMethod.PARAMETRIC)
        mu = sum(returns) / len(returns)
        var_vals = returns
        n = len(var_vals)
        sigma = math.sqrt(sum((v - mu) ** 2 for v in var_vals) / (n - 1))
        from statistics import NormalDist

        z = NormalDist().inv_cdf(0.95)
        expected = -mu + z * sigma
        assert results[0].var == pytest.approx(expected, rel=1e-6)

    def test_parametric_cvar_ge_var(self):
        sim = RiskSimulator()
        results = sim.calculate_var(gen_returns(100), method=RiskMethod.PARAMETRIC)
        for vr in results:
            assert vr.cvar >= vr.var - 1e-9

    def test_zero_variance(self):
        """零方差(所有收益相同)→ VaR=max(0,-mean)。"""
        sim = RiskSimulator()
        results = sim.calculate_var([0.001] * 50, confidence_levels=[0.95], method=RiskMethod.PARAMETRIC)
        assert results[0].var == pytest.approx(0.0, abs=1e-9)


# ============== 蒙特卡洛 VaR ==============


class TestMonteCarloVaR:
    def test_mc_var_positive(self):
        sim = RiskSimulator()
        results = sim.calculate_var(gen_returns(100), confidence_levels=[0.95], method=RiskMethod.MONTE_CARLO)
        assert results[0].var > 0
        assert results[0].method == RiskMethod.MONTE_CARLO

    def test_mc_reproducible(self):
        """同 seed 蒙特卡洛结果可复现。"""
        sim = RiskSimulator()
        r1 = sim.calculate_var(gen_returns(100), confidence_levels=[0.95], method=RiskMethod.MONTE_CARLO)
        r2 = sim.calculate_var(gen_returns(100), confidence_levels=[0.95], method=RiskMethod.MONTE_CARLO)
        assert r1[0].var == pytest.approx(r2[0].var, rel=1e-9)

    def test_mc_close_to_parametric(self):
        """蒙特卡洛 VaR 应接近参数 VaR(同正态假设)。"""
        sim = RiskSimulator(RiskConfig(mc_paths=50000))
        returns = gen_returns(200, mean=0.001, std=0.01, seed=3)
        mc = sim.calculate_var(returns, confidence_levels=[0.95], method=RiskMethod.MONTE_CARLO)
        par = sim.calculate_var(returns, confidence_levels=[0.95], method=RiskMethod.PARAMETRIC)
        # 5% 容差
        assert mc[0].var == pytest.approx(par[0].var, rel=0.05)


# ============== 回撤模拟 ==============


class TestDrawdown:
    def test_max_drawdown_value(self):
        sim = RiskSimulator()
        # 10%涨 → 20%跌 → 5%涨
        returns = [0.10, -0.20, 0.05]
        dd = sim.simulate_drawdown(returns)
        # wealth: 1.10, 0.88, 0.924
        # peak=1.10, trough=0.88, max_dd=(0.88-1.10)/1.10=-0.2
        assert dd.max_drawdown == pytest.approx(-0.20, abs=1e-6)

    def test_max_drawdown_non_positive(self):
        sim = RiskSimulator()
        dd = sim.simulate_drawdown(gen_returns(100))
        assert dd.max_drawdown <= 0

    def test_drawdown_duration(self):
        sim = RiskSimulator()
        returns = [0.10, -0.05, -0.10, 0.02]
        # wealth: 1.10, 1.045, 0.9405, 0.95931
        # peak at idx0=1.10, trough at idx2=0.9405, duration=2-0=2
        dd = sim.simulate_drawdown(returns)
        assert dd.max_dd_duration == 2

    def test_recovery(self):
        sim = RiskSimulator()
        # 跌后回升至峰
        returns = [0.10, -0.05, 0.06, 0.10]
        # wealth: 1.10, 1.045, 1.1077, 1.21847
        # peak idx0=1.10, trough idx1=1.045, recovery at idx2 (1.1077>1.10)
        dd = sim.simulate_drawdown(returns)
        assert dd.recovery_duration == 1

    def test_no_recovery(self):
        sim = RiskSimulator()
        # 跌后未回升
        returns = [0.10, -0.20, -0.05]
        dd = sim.simulate_drawdown(returns)
        assert dd.recovery_duration is None

    def test_all_positive_no_drawdown(self):
        sim = RiskSimulator()
        returns = [0.05, 0.05, 0.05]
        dd = sim.simulate_drawdown(returns)
        assert dd.max_drawdown == pytest.approx(0.0, abs=1e-9)
        assert dd.current_drawdown == pytest.approx(0.0, abs=1e-9)

    def test_current_drawdown(self):
        sim = RiskSimulator()
        returns = [0.10, -0.05]
        # wealth: 1.10, 1.045; global_peak=1.10; current=(1.045-1.10)/1.10
        dd = sim.simulate_drawdown(returns)
        assert dd.current_drawdown == pytest.approx((1.045 - 1.10) / 1.10, abs=1e-6)


# ============== 熔断模拟 ==============


class TestCircuitBreaker:
    def test_triggered(self):
        sim = RiskSimulator()
        returns = [0.10, -0.20, 0.05]  # max_dd=-0.20
        cb = sim.simulate_circuit_breaker(returns, trigger_level=-0.10)
        assert cb.triggered is True
        assert cb.hit_count >= 1

    def test_not_triggered(self):
        sim = RiskSimulator()
        returns = [0.05, 0.05, 0.05]  # 无回撤
        cb = sim.simulate_circuit_breaker(returns, trigger_level=-0.10)
        assert cb.triggered is False
        assert cb.hit_count == 0

    def test_worst_drawdown(self):
        sim = RiskSimulator()
        returns = [0.10, -0.20, 0.05]
        cb = sim.simulate_circuit_breaker(returns, trigger_level=-0.10)
        assert cb.worst_drawdown == pytest.approx(-0.20, abs=1e-6)

    def test_trigger_level_recorded(self):
        sim = RiskSimulator()
        cb = sim.simulate_circuit_breaker(gen_returns(50), trigger_level=-0.15)
        assert cb.trigger_level == -0.15

    def test_multiple_hits(self):
        """多次跌破阈值(两段)。"""
        sim = RiskSimulator()
        # 涨→大跌→涨→大跌
        returns = [0.05, -0.15, 0.20, -0.15]
        cb = sim.simulate_circuit_breaker(returns, trigger_level=-0.10)
        assert cb.hit_count >= 1


# ============== 全量仿真 ==============


class TestFullSimulation:
    def test_full_result_populated(self):
        sim = RiskSimulator()
        result = sim.run_full_simulation(gen_returns(100))
        assert isinstance(result, RiskSimulationResult)
        assert len(result.var_results) == 2
        assert result.drawdown is not None
        assert result.circuit_breaker is not None
        assert result.num_obs == 100
        assert result.method == RiskMethod.HISTORICAL

    def test_full_with_method(self):
        sim = RiskSimulator()
        result = sim.run_full_simulation(gen_returns(100), method=RiskMethod.PARAMETRIC)
        assert result.method == RiskMethod.PARAMETRIC
        assert all(vr.method == RiskMethod.PARAMETRIC for vr in result.var_results)


# ============== 边界值 ==============


class TestEdgeCases:
    def test_empty_raises(self):
        sim = RiskSimulator()
        with pytest.raises(SimulationError):
            sim.calculate_var([])

    def test_single_sample_raises(self):
        sim = RiskSimulator()
        with pytest.raises(SimulationError):
            sim.calculate_var([0.01])

    def test_empty_drawdown_raises(self):
        sim = RiskSimulator()
        with pytest.raises(SimulationError):
            sim.simulate_drawdown([])

    def test_empty_breaker_raises(self):
        sim = RiskSimulator()
        with pytest.raises(SimulationError):
            sim.simulate_circuit_breaker([])

    def test_error_code(self):
        assert SimulationError.error_code == "ZA-SIM-0003"


# ============== 枚举 ==============


class TestEnums:
    def test_method_values(self):
        assert RiskMethod.HISTORICAL.value == "historical"
        assert RiskMethod.PARAMETRIC.value == "parametric"
        assert RiskMethod.MONTE_CARLO.value == "monte_carlo"

    def test_enum_is_str(self):
        assert isinstance(RiskMethod.HISTORICAL, str)


# ============== 配置只读 ==============


class TestConfigReadonly:
    def test_config_property(self):
        cfg = RiskConfig(mc_paths=500)
        sim = RiskSimulator(cfg)
        assert sim.config.mc_paths == 500
        assert sim.config is cfg


# ============== 审计摘要 ==============


class TestAuditSummary:
    def test_summary_contains_var(self):
        sim = RiskSimulator()
        result = sim.run_full_simulation(gen_returns(100))
        summary = sim.audit_summary(result)
        assert "VaR" in summary
        assert "回撤" in summary
        assert "熔断" in summary

    def test_summary_contains_method(self):
        sim = RiskSimulator()
        result = sim.run_full_simulation(gen_returns(50), method=RiskMethod.PARAMETRIC)
        summary = sim.audit_summary(result)
        assert "parametric" in summary
