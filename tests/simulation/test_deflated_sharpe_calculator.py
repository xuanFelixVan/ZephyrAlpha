# [BLUEPRINT] MOD-SIM-024 | docs/03_modules/_domain_simulation/deflated_sharpe_calculator/blueprint.md
# [MODULE] tests.simulation.test_deflated_sharpe_calculator
# [DOMAIN] D_SIMULATION
# [DEPENDENCIES] zephyr.simulation.deflated_sharpe_calculator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SIM-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-SIM-024 Deflated Sharpe Ratio Calculator 单元测试.

覆盖: 基本DSR计算、N=1无修正、N>1多重测试修正、偏度/峰度影响、
显著性判定、趋势追踪、边界值(空序列/样本不足/年化)、已知值验证.
"""

from __future__ import annotations

import math
import random

import pytest

from zephyr.simulation.deflated_sharpe_calculator import (
    DeflatedSharpeCalculator,
    DSRConfig,
    DSRResult,
    DSRTrendPoint,
    SimulationError,
)

# ============== 辅助函数 ==============


def gen_normal(n: int, mean: float = 0.001, std: float = 0.02, seed: int = 42) -> list[float]:
    """生成正态分布收益率序列。"""
    rng = random.Random(seed)
    return [rng.gauss(mean, std) for _ in range(n)]


# ============== 基本计算 ==============


class TestBasicCalculation:
    def test_calculate_returns_result(self):
        calc = DeflatedSharpeCalculator()
        result = calc.calculate(gen_normal(100), num_trials=1)
        assert isinstance(result, DSRResult)
        assert 0.0 < result.dsr < 1.0

    def test_sharpe_positive_for_positive_mean(self):
        calc = DeflatedSharpeCalculator()
        result = calc.calculate(gen_normal(200, mean=0.001, std=0.01), num_trials=1)
        assert result.sharpe > 0

    def test_sharpe_negative_for_negative_mean(self):
        calc = DeflatedSharpeCalculator()
        # 均值=-0.01 标准差=0.01 -> 期望Sharpe=-1.0, 可靠为负
        result = calc.calculate(gen_normal(500, mean=-0.01, std=0.01, seed=42), num_trials=1)
        assert result.sharpe < 0

    def test_annualized_sharpe(self):
        calc = DeflatedSharpeCalculator(DSRConfig(periods_per_year=252))
        result = calc.calculate(gen_normal(200, seed=1), num_trials=1)
        assert result.sharpe_annualized == pytest.approx(result.sharpe * math.sqrt(252), rel=1e-6)

    def test_dsr_in_range(self):
        calc = DeflatedSharpeCalculator()
        for seed in range(10):
            result = calc.calculate(gen_normal(100, seed=seed), num_trials=1)
            assert 0.0 < result.dsr < 1.0

    def test_result_fields_populated(self):
        calc = DeflatedSharpeCalculator()
        result = calc.calculate(gen_normal(100), num_trials=5)
        assert result.num_trials == 5
        assert result.num_obs == 100
        assert isinstance(result.skewness, float)
        assert isinstance(result.kurtosis, float)
        assert isinstance(result.var_sr, float)
        assert isinstance(result.expected_max, float)
        assert isinstance(result.is_significant, bool)


# ============== N=1 vs N>1 (多重测试修正) ==============


class TestMultipleTestingCorrection:
    def test_n1_no_correction(self):
        """N=1 时 expected_max=0, 无多重测试修正。"""
        calc = DeflatedSharpeCalculator()
        result = calc.calculate(gen_normal(100), num_trials=1)
        assert result.expected_max == 0.0

    def test_n_greater_1_reduces_dsr(self):
        """试次数越多, DSR 越低(多重测试惩罚)。"""
        calc = DeflatedSharpeCalculator()
        returns = gen_normal(200, mean=0.001, seed=7)
        dsr_1 = calc.calculate(returns, num_trials=1).dsr
        dsr_10 = calc.calculate(returns, num_trials=10).dsr
        dsr_100 = calc.calculate(returns, num_trials=100).dsr
        assert dsr_1 >= dsr_10 >= dsr_100

    def test_expected_max_increases_with_n(self):
        """E[max] 随 N 增大而增大。"""
        calc = DeflatedSharpeCalculator()
        returns = gen_normal(100)
        e1 = calc.calculate(returns, num_trials=1).expected_max
        e10 = calc.calculate(returns, num_trials=10).expected_max
        e100 = calc.calculate(returns, num_trials=100).expected_max
        assert e1 < e10 < e100

    def test_expected_max_known_value(self):
        """N=2: E[max] ≈ sqrt(2*ln2) - (ln(pi)+ln(ln2))/(2*sqrt(2*ln2))"""
        from zephyr.simulation.deflated_sharpe_calculator import _expected_max_sharpe

        val = _expected_max_sharpe(2)
        ln_n = math.log(2)
        expected = math.sqrt(2 * ln_n) - (math.log(math.pi) + math.log(ln_n)) / (2 * math.sqrt(2 * ln_n))
        assert val == pytest.approx(expected, rel=1e-6)


# ============== 显著性判定 ==============


class TestSignificance:
    def test_significant_with_high_sharpe_low_trials(self):
        calc = DeflatedSharpeCalculator(DSRConfig(significance_threshold=0.5))
        # 高均值低波动 -> 高 Sharpe -> 高 DSR
        result = calc.calculate(gen_normal(200, mean=0.005, std=0.005), num_trials=1)
        assert result.is_significant is True

    def test_not_significant_with_high_trials(self):
        calc = DeflatedSharpeCalculator(DSRConfig(significance_threshold=0.95))
        # 低 Sharpe + 很多试次 -> DSR 被压低
        result = calc.calculate(gen_normal(100, mean=0.0001, std=0.02), num_trials=1000)
        assert result.is_significant is False

    def test_threshold_configurable(self):
        calc_low = DeflatedSharpeCalculator(DSRConfig(significance_threshold=0.01))
        calc_high = DeflatedSharpeCalculator(DSRConfig(significance_threshold=0.99))
        returns = gen_normal(100, seed=3)
        r_low = calc_low.calculate(returns, num_trials=1)
        r_high = calc_high.calculate(returns, num_trials=1)
        # 同样的 DSR, 低阈值更可能显著
        if 0.01 < r_low.dsr < 0.99:
            assert r_low.is_significant is True
            assert r_high.is_significant is False


# ============== 趋势追踪 ==============


class TestTrendTracking:
    def test_track_trend_length(self):
        calc = DeflatedSharpeCalculator()
        returns = gen_normal(200)
        trend = calc.track_trend(returns, num_trials=1, window=60)
        assert len(trend) == 200 - 60 + 1

    def test_track_trend_points(self):
        calc = DeflatedSharpeCalculator()
        returns = gen_normal(150)
        trend = calc.track_trend(returns, num_trials=5, window=60)
        assert all(isinstance(p, DSRTrendPoint) for p in trend)
        assert all(0.0 < p.dsr < 1.0 for p in trend)
        assert all(p.index >= 59 for p in trend)

    def test_track_trend_window_too_small(self):
        calc = DeflatedSharpeCalculator()
        with pytest.raises(SimulationError, match="window"):
            calc.track_trend(gen_normal(100), window=2)

    def test_track_trend_sequence_too_short(self):
        calc = DeflatedSharpeCalculator()
        with pytest.raises(SimulationError, match="序列长度"):
            calc.track_trend(gen_normal(50), window=60)


# ============== 边界值 / 错误处理 ==============


class TestEdgeCases:
    def test_empty_returns_rejected(self):
        calc = DeflatedSharpeCalculator()
        with pytest.raises(SimulationError, match="不能为空"):
            calc.calculate([], num_trials=1)

    def test_insufficient_samples_rejected(self):
        calc = DeflatedSharpeCalculator()
        with pytest.raises(SimulationError, match="样本数不足"):
            calc.calculate([0.01, 0.02], num_trials=1)

    def test_num_trials_zero_rejected(self):
        calc = DeflatedSharpeCalculator()
        with pytest.raises(SimulationError, match="num_trials"):
            calc.calculate(gen_normal(100), num_trials=0)

    def test_zero_variance_returns(self):
        """所有收益率相同 -> std=0 -> Sharpe=0"""
        calc = DeflatedSharpeCalculator()
        result = calc.calculate([0.001] * 100, num_trials=1)
        assert result.sharpe == 0.0

    def test_risk_free_rate_override(self):
        calc = DeflatedSharpeCalculator(DSRConfig(risk_free_rate=0.0))
        returns = gen_normal(100, mean=0.001, seed=5)
        r1 = calc.calculate(returns, num_trials=1, risk_free_rate=0.0)
        r2 = calc.calculate(returns, num_trials=1, risk_free_rate=0.001)
        assert r1.sharpe != r2.sharpe

    def test_config_default_used(self):
        calc = DeflatedSharpeCalculator(DSRConfig(risk_free_rate=0.0005))
        returns = gen_normal(100, mean=0.001, seed=5)
        r_default = calc.calculate(returns, num_trials=1)
        r_explicit = calc.calculate(returns, num_trials=1, risk_free_rate=0.0005)
        assert r_default.sharpe == pytest.approx(r_explicit.sharpe, rel=1e-9)


# ============== 统计函数 ==============


class TestStatistics:
    def test_skewness_symmetric_normal_near_zero(self):
        from zephyr.simulation.deflated_sharpe_calculator import _skewness

        # 大样本正态分布偏度接近0
        returns = gen_normal(10000, mean=0, std=1, seed=99)
        sk = _skewness(returns)
        assert abs(sk) < 0.2

    def test_kurtosis_normal_near_zero(self):
        from zephyr.simulation.deflated_sharpe_calculator import _kurtosis

        returns = gen_normal(10000, mean=0, std=1, seed=99)
        ku = _kurtosis(returns)
        assert abs(ku) < 0.3  # 超额峰度接近0

    def test_variance_of_sharpe_formula(self):
        from zephyr.simulation.deflated_sharpe_calculator import _variance_of_sharpe

        # SR=0, γ=0, κ=0, T=100 -> V = 1/99
        v = _variance_of_sharpe(0.0, 0.0, 0.0, 100)
        assert v == pytest.approx(1.0 / 99, rel=1e-6)

    def test_normal_cdf_known_values(self):
        from zephyr.simulation.deflated_sharpe_calculator import _normal_cdf

        assert _normal_cdf(0.0) == pytest.approx(0.5, abs=1e-9)
        assert _normal_cdf(-10.0) == pytest.approx(0.0, abs=1e-9)
        assert _normal_cdf(10.0) == pytest.approx(1.0, abs=1e-9)


# ============== 不可变性 ==============


class TestImmutability:
    def test_result_frozen(self):
        calc = DeflatedSharpeCalculator()
        result = calc.calculate(gen_normal(100), num_trials=1)
        with pytest.raises(Exception):
            result.dsr = 0.5  # type: ignore[misc]

    def test_config_frozen(self):
        cfg = DSRConfig()
        with pytest.raises(Exception):
            cfg.significance_threshold = 0.99  # type: ignore[misc]
