# [BLUEPRINT] MOD-SIGQC-005 | docs/03_modules/_domain_signal_quality/signal_quality_benchmark/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIGQC-005 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.signal_quality.test_signal_quality_benchmark
# [TESTS] src/zephyr/signal_quality/signal_quality_benchmark.py
"""MOD-SIGQC-005 单元测试：signal_quality_benchmark 信号质量基准对比器。

蓝图验收（B14-04630/CAND-SIGQC-004，A9 D-SIGNAL-157）：
当前 IC/覆盖率/稳定性 vs 滚动历史基线与基准策略（buy-hold 语义注入基准序
列）+ 偏离超阈告警 + 周度对比报告。基准序列/告警 sink 全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.signal_quality.signal_quality_benchmark",
    reason="signal_quality_benchmark not importable",
)

from zephyr.signal_quality.signal_quality_benchmark import (  # noqa: E402
    QualitySnapshot,
    SignalBenchmarkError,
    SignalQualityBenchmark,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)  # 周三
_T1 = datetime.datetime(2026, 8, 27, 9, 30, 0)  # 周四（同 ISO 周）
_T2 = datetime.datetime(2026, 9, 2, 9, 30, 0)  # 次周周三


def _snap(
    strategy_id: str = "alpha-1",
    *,
    ic: float = 0.10,
    coverage: float = 0.8,
    stability: float = 0.9,
    at: datetime.datetime = _T0,
) -> QualitySnapshot:
    return QualitySnapshot(
        strategy_id=strategy_id,
        ic=ic,
        coverage=coverage,
        stability=stability,
        recorded_at=at,
    )


def _bench(alerts: list | None = None, benchmark=(0.03, 0.05, 0.04), **kwargs) -> SignalQualityBenchmark:
    return SignalQualityBenchmark(
        benchmark_series=benchmark,
        clock=lambda: _T0,
        alert_sink=(lambda d: alerts.append(d)) if alerts is not None else None,
        **kwargs,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 当前 vs 历史基线 vs 基准策略（正常路径）
# ──────────────────────────────────────────────────────────────────────────────


class TestCompare:
    def test_benchmark_mean(self) -> None:
        b = _bench()
        assert b.benchmark_mean == pytest.approx(0.04)

    def test_compare_no_deviation_no_alert(self) -> None:
        alerts: list = []
        b = _bench(alerts)
        b.record(_snap(ic=0.10, coverage=0.8, stability=0.9, at=_T0))
        b.record(_snap(ic=0.11, coverage=0.82, stability=0.88, at=_T1))
        cmp = b.compare("alpha-1")
        assert cmp.baseline_size == 1
        assert cmp.baseline_ic == pytest.approx(0.10)
        assert cmp.current_ic == pytest.approx(0.11)
        assert cmp.ic_deviation_vs_baseline == pytest.approx(0.01)
        assert cmp.ic_deviation_vs_benchmark == pytest.approx(0.07)
        assert cmp.alerts == ()
        assert alerts == []
        assert cmp.compared_at == _T0

    def test_baseline_rolling_window(self) -> None:
        b = _bench(baseline_window=2)
        b.record(_snap(ic=0.50, at=_T0))  # 被挤出基线窗
        b.record(_snap(ic=0.10, at=_T0))
        b.record(_snap(ic=0.20, at=_T1))
        b.record(_snap(ic=0.21, at=_T2))  # 当前
        cmp = b.compare("alpha-1")
        assert cmp.baseline_size == 2  # 仅最近 2 期（剔除最新）
        assert cmp.baseline_ic == pytest.approx(0.15)  # mean(0.10, 0.20)

    def test_ic_deviation_vs_baseline_alert(self) -> None:
        alerts: list = []
        b = _bench(alerts, benchmark=(0.25,))  # 基准均值=当前，隔离基线告警
        b.record(_snap(ic=0.10, at=_T0))
        b.record(_snap(ic=0.25, at=_T1))
        cmp = b.compare("alpha-1")
        assert len(cmp.alerts) == 1
        alert = cmp.alerts[0]
        assert alert.kind == "baseline"
        assert alert.metric == "ic"
        assert alert.deviation == pytest.approx(0.15)
        assert alert.reference == pytest.approx(0.10)
        assert alert.threshold == pytest.approx(0.1)
        assert alert.raised_at == _T0
        assert alerts == list(cmp.alerts)

    def test_coverage_deviation_alert(self) -> None:
        alerts: list = []
        b = _bench(alerts, benchmark=(0.10,))
        b.record(_snap(ic=0.10, coverage=0.8, at=_T0))
        b.record(_snap(ic=0.10, coverage=0.6, at=_T1))
        cmp = b.compare("alpha-1")
        assert len(cmp.alerts) == 1
        assert cmp.alerts[0].metric == "coverage"
        assert cmp.alerts[0].deviation == pytest.approx(-0.2)

    def test_stability_deviation_alert(self) -> None:
        alerts: list = []
        b = _bench(alerts, benchmark=(0.10,))
        b.record(_snap(ic=0.10, stability=0.9, at=_T0))
        b.record(_snap(ic=0.10, stability=0.7, at=_T1))
        cmp = b.compare("alpha-1")
        assert len(cmp.alerts) == 1
        assert cmp.alerts[0].metric == "stability"

    def test_benchmark_deviation_alert(self) -> None:
        alerts: list = []
        b = _bench(alerts, benchmark=(0.0,))  # buy-hold 基准 IC 均值 0
        b.record(_snap(ic=0.10, at=_T0))
        b.record(_snap(ic=0.11, at=_T1))
        cmp = b.compare("alpha-1")
        assert len(cmp.alerts) == 1
        alert = cmp.alerts[0]
        assert alert.kind == "benchmark"
        assert alert.metric == "ic"
        assert alert.deviation == pytest.approx(0.11)

    def test_threshold_strictly_greater_no_alert(self) -> None:
        b = _bench(benchmark=(0.20,))
        b.record(_snap(ic=0.10, at=_T0))
        b.record(_snap(ic=0.20, at=_T1))  # 基线偏离恰 0.1，严格大于方告警
        cmp = b.compare("alpha-1")
        assert cmp.ic_deviation_vs_baseline == pytest.approx(0.1)
        assert cmp.alerts == ()

    def test_multiple_deviations_alerted(self) -> None:
        alerts: list = []
        b = _bench(alerts, benchmark=(0.30,))
        b.record(_snap(ic=0.10, coverage=0.8, stability=0.9, at=_T0))
        b.record(_snap(ic=0.30, coverage=0.5, stability=0.6, at=_T1))
        cmp = b.compare("alpha-1")
        assert [a.metric for a in cmp.alerts] == ["ic", "coverage", "stability"]
        assert all(a.kind == "baseline" for a in cmp.alerts)
        assert len(alerts) == 3

    def test_alert_sink_failure_not_blocking(self) -> None:
        def _bad_sink(_deviation) -> None:
            raise RuntimeError("告警通道故障")

        b = SignalQualityBenchmark(
            benchmark_series=(0.0,), clock=lambda: _T0, alert_sink=_bad_sink
        )
        b.record(_snap(ic=0.10, at=_T0))
        b.record(_snap(ic=0.30, at=_T1))
        cmp = b.compare("alpha-1")  # 告警失败不阻断
        assert len(cmp.alerts) == 2  # baseline.ic + benchmark.ic

    def test_deterministic_replay(self) -> None:
        b1, b2 = _bench(), _bench()
        for b in (b1, b2):
            b.record(_snap(ic=0.10, coverage=0.8, stability=0.9, at=_T0))
            b.record(_snap(ic=0.30, coverage=0.5, stability=0.6, at=_T1))
        c1, c2 = b1.compare("alpha-1"), b2.compare("alpha-1")
        assert c1 == c2
        assert b1.weekly_report("alpha-1") == b2.weekly_report("alpha-1")


# ──────────────────────────────────────────────────────────────────────────────
# 周度对比报告
# ──────────────────────────────────────────────────────────────────────────────


class TestWeeklyReport:
    def test_single_week_aggregation(self) -> None:
        b = _bench()
        b.record(_snap(ic=0.10, coverage=0.8, stability=0.9, at=_T0))
        b.record(_snap(ic=0.20, coverage=0.6, stability=0.7, at=_T1))
        report = b.weekly_report("alpha-1")
        assert report.strategy_id == "alpha-1"
        assert report.benchmark_ic == pytest.approx(0.04)
        assert report.generated_at == _T0
        assert len(report.weeks) == 1
        entry = report.weeks[0]
        assert (entry.iso_year, entry.iso_week) == (
            _T0.isocalendar().year,
            _T0.isocalendar().week,
        )
        assert entry.sample_size == 2
        assert entry.ic_mean == pytest.approx(0.15)
        assert entry.coverage_mean == pytest.approx(0.7)
        assert entry.stability_mean == pytest.approx(0.8)
        assert entry.ic_deviation_vs_benchmark == pytest.approx(0.11)

    def test_two_weeks_sorted(self) -> None:
        b = _bench()
        b.record(_snap(ic=0.10, at=_T2))  # 次周先登记
        b.record(_snap(ic=0.20, at=_T0))
        report = b.weekly_report("alpha-1")
        assert len(report.weeks) == 2
        first, second = report.weeks
        assert (first.iso_year, first.iso_week) < (second.iso_year, second.iso_week)
        assert (first.iso_year, first.iso_week) == (
            _T0.isocalendar().year,
            _T0.isocalendar().week,
        )
        assert (second.iso_year, second.iso_week) == (
            _T2.isocalendar().year,
            _T2.isocalendar().week,
        )
        assert first.ic_mean == pytest.approx(0.20)
        assert second.ic_mean == pytest.approx(0.10)


# ──────────────────────────────────────────────────────────────────────────────
# Fail-Closed 分支
# ──────────────────────────────────────────────────────────────────────────────


class TestFailClosed:
    def test_compare_unknown_strategy_raises(self) -> None:
        with pytest.raises(SignalBenchmarkError):
            _bench().compare("ghost")

    def test_compare_insufficient_history_raises(self) -> None:
        b = _bench()
        b.record(_snap())
        with pytest.raises(SignalBenchmarkError):
            b.compare("alpha-1")

    def test_compare_empty_strategy_id_raises(self) -> None:
        with pytest.raises(SignalBenchmarkError):
            _bench().compare("")

    def test_weekly_report_unknown_strategy_raises(self) -> None:
        with pytest.raises(SignalBenchmarkError):
            _bench().weekly_report("ghost")
        with pytest.raises(SignalBenchmarkError):
            _bench().weekly_report("")

    def test_record_ic_out_of_range_raises(self) -> None:
        b = _bench()
        with pytest.raises(SignalBenchmarkError):
            b.record(_snap(ic=1.1))
        with pytest.raises(SignalBenchmarkError):
            b.record(_snap(ic=-1.1))

    def test_record_coverage_stability_out_of_range_raises(self) -> None:
        b = _bench()
        with pytest.raises(SignalBenchmarkError):
            b.record(_snap(coverage=1.1))
        with pytest.raises(SignalBenchmarkError):
            b.record(_snap(coverage=-0.1))
        with pytest.raises(SignalBenchmarkError):
            b.record(_snap(stability=1.1))
        with pytest.raises(SignalBenchmarkError):
            b.record(_snap(stability=-0.1))

    def test_record_empty_strategy_id_raises(self) -> None:
        with pytest.raises(SignalBenchmarkError):
            _bench().record(_snap(""))

    def test_constructor_empty_benchmark_series_raises(self) -> None:
        with pytest.raises(SignalBenchmarkError):
            _bench(benchmark=())

    def test_constructor_benchmark_value_out_of_range_raises(self) -> None:
        with pytest.raises(SignalBenchmarkError):
            _bench(benchmark=(0.5, 1.2))
        with pytest.raises(SignalBenchmarkError):
            _bench(benchmark=(True,))  # bool 非合法基准值

    def test_constructor_invalid_params_raise(self) -> None:
        with pytest.raises(SignalBenchmarkError):
            _bench(baseline_window=0)
        with pytest.raises(SignalBenchmarkError):
            _bench(deviation_threshold=0.0)
        with pytest.raises(SignalBenchmarkError):
            _bench(deviation_threshold=-0.1)
