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

import logging
import math
import random

import pytest

from zephyr.simulation.deflated_sharpe_calculator import (
    DSR_SIGNIFICANCE_THRESHOLD,
    DSR_UNDECIDABLE,
    EULER_MASCHERONI,
    DeflatedSharpeCalculator,
    DSRConfig,
    DSRResult,
    DSRTrendPoint,
    SimulationError,
    deflated_sharpe_from_moments,
    variance_of_sharpe,
)
from zephyr.simulation.deflated_sharpe_calculator import (
    expected_max_sharpe_z as canonical_expected_max_z,
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
        """E[max(Z_N)] 钉在**解析真值**上，而非钉在实现的近似式上。

        N 个 iid 标准正态的期望最大值有闭式精确值：
          N=1: 0    N=2: 1/√π = 0.5641896    N=3: 3/(2√π) = 0.8462844
        （一般 N 只能数值积分，故用这两个锚。）

        本用例 2026-09-17 随 SDC-3/SDC-4 施工重写：原断言把值钉成
        Euler–Maclaurin 渐近式 √(2lnN)−(lnπ+lnlnN)/(2√(2lnN)) 的自身输出
        （即"实现即真值"的同义反复，永不会失败）。该渐近式只在 N→∞ 收敛，
        N=2 时给 0.846932，比精确值 0.564190 高 +0.283 个 z 单位（超折减 50%）。
        现口径改用论文闭式（Bailey & López de Prado 2014），故此处对拍解析真值。
        """
        from zephyr.simulation.deflated_sharpe_calculator import expected_max_sharpe_z

        assert expected_max_sharpe_z(1) == 0.0
        # 解析锚点（闭式近似的绝对偏差随 N 收敛）
        assert expected_max_sharpe_z(2) == pytest.approx(1.0 / math.sqrt(math.pi), abs=0.05)
        assert expected_max_sharpe_z(3) == pytest.approx(3.0 / (2.0 * math.sqrt(math.pi)), abs=0.01)
        assert expected_max_sharpe_z(10) == pytest.approx(1.5387527, abs=0.05)

    def test_expected_max_not_the_retired_asymptotic(self):
        """回归锁：被废弃的 Euler–Maclaurin 值不得复活（N=2 旧值 0.8469317）。"""
        from zephyr.simulation.deflated_sharpe_calculator import expected_max_sharpe_z

        retired_n2 = 0.8469317055375386
        assert abs(expected_max_sharpe_z(2) - retired_n2) > 0.30

    def test_expected_max_error_shrinks_with_n(self):
        """闭式近似的相对误差随 N 单调收敛到 0（渐近正确性的机检）。"""
        from zephyr.simulation.deflated_sharpe_calculator import expected_max_sharpe_z

        exact = {2: 0.5641895835477563, 3: 0.8462843753086482}
        rel2 = abs(expected_max_sharpe_z(2) - exact[2]) / exact[2]
        rel3 = abs(expected_max_sharpe_z(3) - exact[3]) / exact[3]
        assert rel3 < rel2  # N 越大越准
        assert rel3 < 0.01


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

    def test_variance_of_sharpe_iid_normal_boundary(self):
        """SDC-3 病灶本身：iid 正态（γ=0, 超额峰度=0）必须回落到 Lo(2002)

        ``V[SR]=(1+SR²/2)/(T−1)``。旧码把超额峰度直接进 Pearson 公式，SR² 系数
        取成 −1/4（符号相反），SR=1 时方差恰为理论值一半——本断言把系数钉死。
        """
        from zephyr.simulation.deflated_sharpe_calculator import variance_of_sharpe

        for sr in (0.0, 0.05, 0.1, 0.3, 1.0, 2.0, 5.0):
            for t in (11, 61, 101, 250, 252, 504):
                got = variance_of_sharpe(sr, 0.0, 0.0, t)
                assert got == pytest.approx((1.0 + sr * sr / 2.0) / (t - 1.0), rel=1e-12), (sr, t)

    def test_variance_of_sharpe_uses_pearson_kurtosis(self):
        """超额峰度 κ 进式前要 +3：SR² 系数 =(κ_p−1)/4 =(κ+2)/4。"""
        from zephyr.simulation.deflated_sharpe_calculator import variance_of_sharpe

        sr, t = 0.4, 101
        for kappa_excess in (-2.0, -1.0, 0.0, 1.5, 4.0, 12.0):
            expected = (1.0 + (kappa_excess + 2.0) / 4.0 * sr * sr) / (t - 1.0)
            assert variance_of_sharpe(sr, 0.0, kappa_excess, t) == pytest.approx(expected, rel=1e-12)
        # 手算锚点（与 tests/backtest/test_overfitting_adjudicator.py 共用）：
        # SR=0.1, T=101, γ=0, 超额峰度=0 -> V=(1+0.005)/100=0.01005
        assert variance_of_sharpe(0.1, 0.0, 0.0, 101) == pytest.approx(0.01005, rel=1e-12)

    def test_variance_of_sharpe_skewness_term(self):
        """γ·SR 一次项：负偏度抬高方差、正偏度压低方差（与峰度项独立）。"""
        from zephyr.simulation.deflated_sharpe_calculator import variance_of_sharpe

        sr, t = 0.3, 252
        base = variance_of_sharpe(sr, 0.0, 0.0, t)
        assert variance_of_sharpe(sr, -0.5, 0.0, t) > base
        assert variance_of_sharpe(sr, +0.5, 0.0, t) < base
        # 手算: 1-(-0.5)(0.3)+(3-1)/4*0.09 = 1+0.15+0.045
        assert variance_of_sharpe(sr, -0.5, 0.0, t) == pytest.approx(1.195 / 251, rel=1e-12)

    def test_variance_of_sharpe_degenerate_inputs(self):
        """T≤1 无法估计 -> 0.0 并判退化；退化谓词对 NaN 也成立（不认识即不判）。"""
        from zephyr.simulation.deflated_sharpe_calculator import (
            sharpe_variance_is_degenerate,
            variance_of_sharpe,
        )

        assert variance_of_sharpe(0.1, 0.0, 0.0, 1) == 0.0
        assert variance_of_sharpe(0.1, 0.0, 0.0, 0) == 0.0
        assert sharpe_variance_is_degenerate(0.0) is True
        assert sharpe_variance_is_degenerate(-1.0) is True
        assert sharpe_variance_is_degenerate(float("nan")) is True
        assert sharpe_variance_is_degenerate(1e-9) is False

    def test_normal_cdf_known_values(self):
        from zephyr.simulation.deflated_sharpe_calculator import _normal_cdf

        assert _normal_cdf(0.0) == pytest.approx(0.5, abs=1e-9)
        assert _normal_cdf(-10.0) == pytest.approx(0.0, abs=1e-9)
        assert _normal_cdf(10.0) == pytest.approx(1.0, abs=1e-9)


# ============== 独立预言机对拍（SDC-3 口径的第三方验证）==============


class TestAgainstIndependentOracle:
    """用 stdlib statistics.NormalDist 作独立预言机重算整条 DSR 管线。

    动机（挖矿文档 §3 SDC-3"测试侧"）：官方件历史上只有区间型弱断言，
    SR² 项系数（病灶本身）永不被断言。此处补全链对拍。
    """

    def test_full_pipeline_matches_oracle(self):
        import statistics
        from statistics import NormalDist

        returns = gen_normal(150, mean=0.0012, std=0.015, seed=2026)
        n_trials = 37
        result = DeflatedSharpeCalculator(DSRConfig(periods_per_year=252)).calculate(
            returns, num_trials=n_trials
        )

        # 矩：与实现不同码路（fsum 累加、pstdev 取二阶中心矩），同一定义
        n = len(returns)
        mu = statistics.fmean(returns)
        m2 = statistics.pstdev(returns) ** 2
        m3 = math.fsum((v - mu) ** 3 for v in returns) / n
        m4 = math.fsum((v - mu) ** 4 for v in returns) / n
        gamma_oracle = m3 / m2**1.5
        kappa_excess_oracle = m4 / (m2 * m2) - 3.0

        sr_oracle = mu / statistics.stdev(returns)  # rf=0, ddof=1
        var_sr = (
            1.0
            - gamma_oracle * sr_oracle
            + (kappa_excess_oracle + 3.0 - 1.0) / 4.0 * sr_oracle * sr_oracle  # 显式 +3：Pearson
        ) / (n - 1)
        emax = (1.0 - EULER_MASCHERONI) * NormalDist().inv_cdf(1.0 - 1.0 / n_trials) + EULER_MASCHERONI * (
            NormalDist().inv_cdf(1.0 - 1.0 / (n_trials * math.e))
        )
        oracle_dsr = NormalDist().cdf(sr_oracle / math.sqrt(var_sr) - emax)  # Φ 独立于 math.erf 实现

        assert result.skewness == pytest.approx(gamma_oracle, rel=1e-12)
        assert result.kurtosis == pytest.approx(kappa_excess_oracle, rel=1e-12)
        assert result.sharpe == pytest.approx(sr_oracle, rel=1e-12)
        assert result.var_sr == pytest.approx(var_sr, rel=1e-12)
        assert result.expected_max == pytest.approx(emax, rel=1e-12)
        assert result.dsr == pytest.approx(oracle_dsr, rel=1e-12)
        assert result.degenerate is False

    def test_reported_kurtosis_is_excess_convention(self):
        """结果面 κ 必须是超额口径（正态≈0）——口径翻转会静默改变 DSR。"""
        result = DeflatedSharpeCalculator().calculate(gen_normal(20000, mean=0.0, std=1.0, seed=99), num_trials=1)
        assert abs(result.kurtosis) < 0.2  # 超额：正态→0（若成 Pearson 则 ≈3）
        assert result.kurtosis < 1.0

    def test_iid_normal_sample_lands_on_lo_boundary(self):
        """大样本正态序列的 var_sr 须贴近 Lo(2002) 边界 (1+SR²/2)/(T−1)。"""
        returns = gen_normal(20000, mean=0.001, std=0.02, seed=7)
        result = DeflatedSharpeCalculator().calculate(returns, num_trials=1)
        boundary = (1.0 + result.sharpe**2 / 2.0) / (result.num_obs - 1.0)
        assert result.var_sr == pytest.approx(boundary, rel=2e-2)  # 抽样误差量级


# ============== 退化态 Fail-Closed（SDC-4）==============


class TestDegenerateFailClosed:
    """退化态=没有信息，不得被翻译成"极显著"，也不得被读成"测得不显著"。"""

    def test_inconsistent_moments_are_undecidable(self):
        # γ=3 而超额峰度=0 违反 Pearson 不等式(κ≥γ²−2) ⇒ V[SR]<0 ⇒ 估计失效
        var_sr, dsr, _emax, degenerate = deflated_sharpe_from_moments(
            sharpe=1.0, num_trials=5, num_obs=100, skewness=3.0, excess_kurtosis=0.0
        )
        assert var_sr < 0.0
        assert degenerate is True
        assert dsr == DSR_UNDECIDABLE
        assert dsr < DSR_SIGNIFICANCE_THRESHOLD

    def test_undecidable_emits_warning(self, caplog):
        with caplog.at_level(logging.WARNING, logger="zephyr.simulation.deflated_sharpe_calculator"):
            deflated_sharpe_from_moments(sharpe=1.0, num_trials=5, num_obs=100, skewness=3.0, excess_kurtosis=0.0)
        assert any(rec.levelno == logging.WARNING for rec in caplog.records), "退化态必须出声"

    def test_decidable_case_not_flagged(self):
        """不过度触发：正态可判样本不得被标退化（否则闸门永不放行=另一种失效）。"""
        result = DeflatedSharpeCalculator().calculate(gen_normal(200, mean=0.001, std=0.02), num_trials=10)
        assert result.degenerate is False
        assert 0.0 < result.dsr < 1.0

    def test_never_significant_when_degenerate(self):
        """退化态在任意阈值下都不得判显著（含 threshold→0 的极端配置）。"""
        calc = DeflatedSharpeCalculator(DSRConfig(significance_threshold=1e-9))
        result = calc.calculate([0.001] * 100, num_trials=1)  # 零方差
        assert result.degenerate is True
        assert result.dsr == DSR_UNDECIDABLE
        assert result.is_significant is False

    def test_zero_variance_series_is_undecidable(self, caplog):
        with caplog.at_level(logging.WARNING, logger="zephyr.simulation.deflated_sharpe_calculator"):
            result = DeflatedSharpeCalculator().calculate([0.001] * 100, num_trials=1)
        assert result.degenerate is True
        assert result.dsr == DSR_UNDECIDABLE
        assert result.sharpe == 0.0  # 占位值如实保留，但由 degenerate 说明其含义
        assert any(rec.levelno == logging.WARNING for rec in caplog.records)

    def test_moments_below_estimability_floor_are_undecidable(self):
        """n=3：偏度/峰度返回占位 0.0，不是"测得薄尾" ⇒ 不可判定。"""
        result = DeflatedSharpeCalculator().calculate([0.01, 0.02, -0.005], num_trials=1)
        assert result.degenerate is True
        assert result.dsr == DSR_UNDECIDABLE
        assert result.is_significant is False
        # n=4 起矩可估，不再因样本触达退化分支
        ok = DeflatedSharpeCalculator().calculate([0.01, 0.02, -0.005, 0.004], num_trials=1)
        assert ok.degenerate is False

    def test_track_trend_degenerate_window_flagged_via_dsr_floor(self):
        """趋势追踪里退化窗口落在 0.0（保守地板），不会伪装成显著窗口。"""
        returns = [0.001] * 60 + list(gen_normal(60, mean=0.001, seed=3))
        trend = DeflatedSharpeCalculator().track_trend(returns, num_trials=1, window=60)
        assert all(0.0 <= p.dsr <= 1.0 for p in trend)
        assert any(p.dsr == DSR_UNDECIDABLE for p in trend)  # 前置零方差窗口


# ============== 同族三实现口径一致性（防再分叉锁）==============


class TestCrossImplementationConvergence:
    """三处 DSR（官方件 / 裁定器 / metrics）口径必须同源——任何一处另写公式即红。"""

    def test_variance_of_sharpe_identical_across_implementations(self):
        from zephyr.backtest.core.overfitting_adjudicator import adjudicate_dsr

        for sr in (0.0, 0.05, 0.14, 0.4, 1.0):
            for skew in (0.0, -0.5, 3.0):
                for kurt in (-2.0, 0.0, 1.5, 12.0):
                    for t in (101, 252):
                        expected = variance_of_sharpe(sr, skew, kurt, t)
                        got = adjudicate_dsr(sharpe=sr, num_trials=2, num_obs=t, skewness=skew, kurtosis=kurt).var_sr
                        assert got == pytest.approx(expected, rel=1e-12), (sr, skew, kurt, t)

    def test_dsr_identical_at_single_trial(self):
        """N=1 时 E[max]=0，两实现须逐位相等（纯 V[SR] 口径对拍）。"""
        from zephyr.backtest.core.overfitting_adjudicator import adjudicate_dsr

        returns = gen_normal(250, mean=0.001, std=0.02, seed=5)
        official = DeflatedSharpeCalculator().calculate(returns, num_trials=1)
        verdict = adjudicate_dsr(
            sharpe=official.sharpe,
            num_trials=1,
            num_obs=official.num_obs,
            skewness=official.skewness,
            kurtosis=official.kurtosis,
        )
        assert verdict.dsr == pytest.approx(official.dsr, rel=1e-12)
        assert verdict.degenerate == official.degenerate

    def test_expected_max_shared(self):
        from zephyr.backtest.core.overfitting_adjudicator import expected_max_sharpe_z

        for n in (1, 2, 3, 10, 50, 600, 4497):
            assert expected_max_sharpe_z(n) == pytest.approx(canonical_expected_max_z(n), rel=1e-15)

    def test_metrics_delegates_to_canonical(self, tmp_path):
        import numpy as np
        import pandas as pd

        from zephyr.backtest.core.metrics import calculate_full_metrics

        rng = np.random.default_rng(11)
        rets = 0.001 + rng.normal(0.0, 0.005, 299)
        nav = 1_000_000 * np.cumprod(1 + np.concatenate([[0.0], rets]))
        nav_series = pd.Series(nav, index=pd.date_range("2023-01-02", periods=300, freq="B"))
        assert tmp_path  # 测试不落生产目录（仅占位声明）

        full = calculate_full_metrics(nav_series, trades_count=50, n_trials=10)
        official = DeflatedSharpeCalculator(DSRConfig(periods_per_year=252)).calculate(
            [float(r) for r in nav_series.pct_change().dropna()],
            num_trials=10,
            risk_free_rate=0.025 / 252,
        )
        assert full["dsr"] == pytest.approx(official.dsr, rel=1e-12)
        assert full["dsr_degenerate"] == official.degenerate
        assert full["expected_max_sharpe"] == pytest.approx(official.expected_max, rel=1e-12)


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
