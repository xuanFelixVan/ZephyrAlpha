# [A_test] module_id: MOD-GOV_test_correlation_drift_monitor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.factor.test_correlation_drift_monitor
# [TESTS] src/zephyr/factor/analysis/correlation_drift_monitor.py
# [TTL] task_bound
"""23 号 memo §5.4 相关性漂移监控测试（CUSUM/PSI）。

裁定真源：23_strategy_correlation_validation.md §5.4——
  CUSUM on rolling 63 日 ρ（k=0.5σ/h=4σ）主检测 + PSI（>0.2 调查 / >0.4 告警）
  辅助；σ=0 降级不告警。
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.analysis.correlation_drift_monitor import (
    PsiLevel,
    assess_pair_drift,
    compute_rolling_spearman,
    cusum_upper_alarm,
    population_stability_index,
)


class TestRollingSpearman:
    def test_identical_series_corr_one(self):
        rng = np.random.default_rng(61)
        r = pd.Series(rng.normal(0, 0.01, 120))
        rho = compute_rolling_spearman(r, r, window=63)
        assert rho.iloc[:62].isna().all()  # 预热段
        assert rho.iloc[62:].to_numpy() == pytest.approx(1.0)

    def test_window_and_length_rejected(self):
        s = pd.Series(np.random.default_rng(1).normal(0, 1, 50))
        with pytest.raises(ValueError):
            compute_rolling_spearman(s, s, window=1)
        with pytest.raises(ValueError):
            compute_rolling_spearman(s, s, window=63)  # 样本<窗口


class TestCusumUpperAlarm:
    def test_below_baseline_no_alarm(self):
        """ρ 持续低于基线 → 增量恒负 → S⁺恒 0 → 不告警（确定性契约）。"""
        rng = np.random.default_rng(67)
        rho = pd.Series(rng.normal(0.25, 0.01, 200))  # 低于基线 0.3
        res = cusum_upper_alarm(rho, baseline_rho=0.3)
        assert not res.alarm
        assert res.first_alarm_pos is None
        assert not res.degraded
        assert res.k == pytest.approx(0.5 * rho.std(ddof=1))
        assert res.h == pytest.approx(4.0 * rho.std(ddof=1))
        assert (res.s_plus.dropna() == 0.0).all()

    def test_step_shift_triggers_alarm(self):
        """ρ 从 0.3 结构性跳到 0.6 → CUSUM 必告警且位置在跳变后。"""
        rng = np.random.default_rng(71)
        rho = pd.Series(np.concatenate([rng.normal(0.3, 0.05, 100), rng.normal(0.6, 0.05, 100)]))
        res = cusum_upper_alarm(rho, baseline_rho=0.3)
        assert res.alarm
        assert res.first_alarm_pos is not None and res.first_alarm_pos >= 100
        assert res.s_plus.iloc[-1] > res.h

    def test_constant_series_degraded_no_alarm(self):
        """σ=0 常数 ρ 序列 → degraded 不告警（无法检测）。"""
        res = cusum_upper_alarm(pd.Series([0.3] * 100), baseline_rho=0.3)
        assert res.degraded
        assert not res.alarm

    def test_explicit_params_override(self):
        rng = np.random.default_rng(73)
        rho = pd.Series(rng.normal(0.3, 0.05, 100))
        res = cusum_upper_alarm(rho, baseline_rho=0.3, k=0.01, h=0.02)
        assert res.k == 0.01 and res.h == 0.02
        assert res.alarm  # 极小阈值下随机游走必越界

    def test_empty_rejected(self):
        with pytest.raises(ValueError):
            cusum_upper_alarm(pd.Series(dtype=float), baseline_rho=0.3)


PSI_THRESHOLD_SAFE = 0.2  # 同分布 PSI 应远低于调查线


class TestPopulationStabilityIndex:
    def test_identical_distribution_near_zero(self):
        rng = np.random.default_rng(79)
        base = rng.normal(0.3, 0.05, 500)
        recent = rng.normal(0.3, 0.05, 200)
        assert population_stability_index(base, recent) < PSI_THRESHOLD_SAFE

    def test_shifted_distribution_alerts(self):
        rng = np.random.default_rng(83)
        base = rng.normal(0.3, 0.05, 500)
        recent = rng.normal(0.7, 0.05, 200)  # 分布明显漂移
        assert population_stability_index(base, recent) > 0.4

    def test_constant_baseline_degenerates_zero(self):
        assert population_stability_index([0.3] * 100, [0.5] * 50) == 0.0

    def test_invalid_inputs_rejected(self):
        with pytest.raises(ValueError):
            population_stability_index([], [0.1])
        with pytest.raises(ValueError):
            population_stability_index([0.1] * 10, [0.2] * 10, n_bins=1)


class TestAssessPairDrift:
    def test_combined_report(self):
        rng = np.random.default_rng(89)
        stable = pd.Series(rng.normal(0.25, 0.01, 200))  # 持续低于基线 → CUSUM 不告警
        report = assess_pair_drift(
            stable,
            baseline_rho=0.3,
            baseline_dist=rng.normal(0.3, 0.05, 500),
            recent_dist=rng.normal(0.3, 0.05, 200),
        )
        assert not report.drift_detected
        assert report.psi is not None and report.psi_level is PsiLevel.STABLE

    def test_psi_alert_marks_drift(self):
        rng = np.random.default_rng(97)
        stable = pd.Series(rng.normal(0.3, 0.05, 200))
        report = assess_pair_drift(
            stable,
            baseline_rho=0.3,
            baseline_dist=rng.normal(0.3, 0.05, 500),
            recent_dist=rng.normal(0.8, 0.05, 200),
        )
        assert report.psi_level is PsiLevel.ALERT
        assert report.drift_detected

    def test_without_distribution_psi_none(self):
        rng = np.random.default_rng(101)
        report = assess_pair_drift(pd.Series(rng.normal(0.3, 0.05, 100)), baseline_rho=0.3)
        assert report.psi is None
        assert report.psi_level is PsiLevel.STABLE
