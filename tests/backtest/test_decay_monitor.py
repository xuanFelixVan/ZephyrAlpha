# [BLUEPRINT] MOD-BT-018 | docs/03_modules/_domain_backtest/decay_monitor/blueprint.md | §D-BACKTEST BT-18
# [A_module] module_id=MOD-BT-018 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [A_test] module_id: MOD-BT-018 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.backtest.test_decay_monitor
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
"""DecayMonitor (MOD-BT-018) 测试套件。

覆盖: STABLE/WARNING/DECAYING/CRITICAL 4级告警、短期/长期均值对比、
       趋势检测、增量更新vs批量评估、样本不足、非有限值校验、配置校验。
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.backtest.services.decay_monitor import (
    DecayLevel,
    DecayMonitor,
    DecayMonitorConfig,
    DecayReport,
    InvalidMetricError,
)


@pytest.fixture
def monitor() -> DecayMonitor:
    return DecayMonitor(
        DecayMonitorConfig(
            short_window=5,
            long_window=15,
            warning_threshold=0.15,
            critical_threshold=0.30,
            trend_window=10,
        )
    )


# ──────────────────────────────────────────────────────────────────────────────
# 样本不足
# ──────────────────────────────────────────────────────────────────────────────


class TestInsufficientSamples:
    def test_few_samples_returns_stable(self, monitor: DecayMonitor):
        for v in [1.0, 2.0, 3.0]:
            report = monitor.update(v)
        assert report.level is DecayLevel.STABLE
        assert "insufficient" in report.message

    def test_zero_samples_evaluate(self, monitor: DecayMonitor):
        report = monitor.evaluate(pd.Series([], dtype=float))
        assert report.level is DecayLevel.STABLE
        assert report.samples == 0


# ──────────────────────────────────────────────────────────────────────────────
# STABLE
# ──────────────────────────────────────────────────────────────────────────────


class TestStable:
    def test_stable_when_short_ge_long(self, monitor: DecayMonitor):
        # 短期均值 >= 长期均值 → STABLE
        values = [1.0] * 15
        report = monitor.evaluate(values)
        assert report.level is DecayLevel.STABLE

    def test_improving_performance_is_stable(self, monitor: DecayMonitor):
        # 性能改善 (短期 > 长期) → STABLE
        values = [1.0] * 10 + [2.0] * 5  # 短期高
        report = monitor.evaluate(values)
        assert report.level is DecayLevel.STABLE
        assert report.decay_ratio < 0  # 负=改善


# ──────────────────────────────────────────────────────────────────────────────
# WARNING
# ──────────────────────────────────────────────────────────────────────────────


class TestWarning:
    def test_warning_when_decay_exceeds_threshold(self, monitor: DecayMonitor):
        # 长期均值≈0.9, 短期均值=0.7 → decay_ratio≈0.22 > 0.15 → WARNING
        values = [1.0] * 10 + [0.7] * 5
        report = monitor.evaluate(values)
        assert report.level is DecayLevel.WARNING
        assert report.decay_ratio > 0.15


# ──────────────────────────────────────────────────────────────────────────────
# CRITICAL
# ──────────────────────────────────────────────────────────────────────────────


class TestCritical:
    def test_critical_when_decay_exceeds_critical(self, monitor: DecayMonitor):
        # 长期均值=1.0, 短期均值=0.6 → decay_ratio=0.4 > 0.30 → CRITICAL
        values = [1.0] * 10 + [0.6] * 5
        report = monitor.evaluate(values)
        assert report.level is DecayLevel.CRITICAL
        assert report.decay_ratio > 0.30

    def test_critical_when_short_term_negative(self, monitor: DecayMonitor):
        # 短期均值为负 → CRITICAL
        values = [1.0] * 10 + [-0.5] * 5
        report = monitor.evaluate(values)
        assert report.level is DecayLevel.CRITICAL


# ──────────────────────────────────────────────────────────────────────────────
# DECAYING (趋势检测)
# ──────────────────────────────────────────────────────────────────────────────


class TestDecayingTrend:
    def test_declining_trend_detected(self, monitor: DecayMonitor):
        # 持续下降趋势 → 至少 DECAYING
        values = np.linspace(2.0, 0.5, 15).tolist()
        report = monitor.evaluate(values)
        assert report.trend_slope < 0
        # 持续下降 + 短期低于长期 → 可能 WARNING/CRITICAL/DECAYING
        assert report.level is not DecayLevel.STABLE

    def test_flat_trend_no_decaying(self, monitor: DecayMonitor):
        values = [1.0] * 15
        report = monitor.evaluate(values)
        assert abs(report.trend_slope) < 1e-10


# ──────────────────────────────────────────────────────────────────────────────
# 增量更新 vs 批量评估
# ──────────────────────────────────────────────────────────────────────────────


class TestUpdateVsEvaluate:
    def test_update_and_evaluate_consistent(self, monitor: DecayMonitor):
        values = [1.0] * 10 + [0.7] * 5
        # 增量更新
        report_update = None
        for v in values:
            report_update = monitor.update(v)
        # 批量评估
        report_eval = monitor.evaluate(values)
        assert report_update is not None
        assert report_update.level is report_eval.level
        assert pytest.approx(report_update.short_term_mean) == report_eval.short_term_mean
        assert pytest.approx(report_update.long_term_mean) == report_eval.long_term_mean

    def test_reset_clears_history(self, monitor: DecayMonitor):
        for v in [1.0] * 10:
            monitor.update(v)
        assert len(monitor.history) == 10
        monitor.reset()
        assert len(monitor.history) == 0
        report = monitor.update(1.0)
        assert report.samples == 1


# ──────────────────────────────────────────────────────────────────────────────
# 输入校验
# ──────────────────────────────────────────────────────────────────────────────


class TestInputValidation:
    def test_nan_metric_raises(self, monitor: DecayMonitor):
        with pytest.raises(InvalidMetricError, match="must be finite"):
            monitor.update(float("nan"))

    def test_inf_metric_raises(self, monitor: DecayMonitor):
        with pytest.raises(InvalidMetricError, match="must be finite"):
            monitor.update(float("inf"))

    def test_evaluate_with_nan_raises(self, monitor: DecayMonitor):
        with pytest.raises(InvalidMetricError, match="non-finite"):
            monitor.evaluate([1.0, float("nan"), 3.0])

    def test_invalid_config_raises(self):
        with pytest.raises(InvalidMetricError):
            DecayMonitorConfig(short_window=10, long_window=5)  # short >= long
        with pytest.raises(InvalidMetricError):
            DecayMonitorConfig(warning_threshold=0.5, critical_threshold=0.3)  # warn > crit


# ──────────────────────────────────────────────────────────────────────────────
# DecayLevel
# ──────────────────────────────────────────────────────────────────────────────


class TestDecayLevel:
    def test_severity_ordering(self):
        # 新顺序: STABLE < DECAYING(趋势预警) < WARNING(衰减超阈值) < CRITICAL
        assert DecayLevel.STABLE.severity < DecayLevel.DECAYING.severity
        assert DecayLevel.DECAYING.severity < DecayLevel.WARNING.severity
        assert DecayLevel.WARNING.severity < DecayLevel.CRITICAL.severity

    def test_worst(self):
        assert DecayLevel.worst([DecayLevel.STABLE, DecayLevel.WARNING]) is DecayLevel.WARNING
        assert DecayLevel.worst([DecayLevel.WARNING, DecayLevel.CRITICAL]) is DecayLevel.CRITICAL
        assert DecayLevel.worst([]) is DecayLevel.STABLE


# ──────────────────────────────────────────────────────────────────────────────
# 综合
# ──────────────────────────────────────────────────────────────────────────────


class TestIntegration:
    def test_realistic_decay_scenario(self):
        """模拟策略从稳定到衰减的全过程。"""
        # 固定种子：噪声 ±0.1 相对基线 1.5 约 6.7%，与 DECAYING 的 trend_magnitude
        # 阈值 5% 接近，未设种子时阶段1 随机趋势可能触发 DECAYING 致 flaky。
        np.random.seed(0)
        monitor = DecayMonitor(
            DecayMonitorConfig(
                short_window=10,
                long_window=30,
                warning_threshold=0.15,
                critical_threshold=0.30,
                trend_window=20,
            )
        )
        # 阶段1: 稳定期 (Sharpe ~1.5)
        for _ in range(30):
            r = monitor.update(1.5 + np.random.uniform(-0.1, 0.1))
        assert r.level is DecayLevel.STABLE

        # 阶段2: 衰减期 (Sharpe 逐渐降至 0.5)
        for _ in range(20):
            r = monitor.update(0.5 + np.random.uniform(-0.1, 0.1))
        assert r.level is not DecayLevel.STABLE
        assert r.is_decaying

    def test_report_is_decaying_property(self, monitor: DecayMonitor):
        values = [1.0] * 15
        report = monitor.evaluate(values)
        assert report.is_decaying is False  # STABLE

        values = [1.0] * 10 + [0.5] * 5
        report = monitor.evaluate(values)
        assert report.is_decaying is True  # CRITICAL or WARNING
