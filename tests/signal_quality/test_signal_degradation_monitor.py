# [BLUEPRINT] MOD-SIGQC-004 | docs/03_modules/_domain_signal_quality/signal_degradation_monitor/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIGQC-004 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.signal_quality.test_signal_degradation_monitor
# [TESTS] src/zephyr/signal_quality/signal_degradation_monitor.py
"""MOD-SIGQC-004 单元测试：signal_degradation_monitor 信号质量退化监控器。

蓝图验收（B13-04309/CAND-SIGQC-003，A3 D-SIGNAL-156）：
质量指标（命中率/IC/衰减）滚动窗跟踪 + 阈值判定 worst-of 分级 + 自动告警
（注入 alert_router）+ 降级信号标记（联动消费端降权语义）+ 不阻断流水线。
告警路由/降权标记全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.signal_quality.signal_degradation_monitor",
    reason="signal_degradation_monitor not importable",
)

from zephyr.signal_quality.signal_degradation_monitor import (  # noqa: E402
    DegradationLevel,
    QualityObservation,
    SignalDegradationError,
    SignalDegradationMonitor,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)


def _obs(
    signal_id: str = "sig-1",
    *,
    hit: bool = True,
    ic: float = 0.05,
    at: datetime.datetime = _T0,
) -> QualityObservation:
    return QualityObservation(signal_id=signal_id, hit=hit, ic=ic, observed_at=at)


def _monitor(
    alerts: list | None = None,
    marks: list | None = None,
    **kwargs,
) -> SignalDegradationMonitor:
    return SignalDegradationMonitor(
        clock=lambda: _T0,
        alert_router=(lambda a: alerts.append(a)) if alerts is not None else None,
        mark_sink=(lambda s, lv, w: marks.append((s, lv, w))) if marks is not None else None,
        **kwargs,
    )


def _feed(monitor: SignalDegradationMonitor, signal_id: str, hits: list[bool], ics: list[float]) -> None:
    for hit, ic in zip(hits, ics, strict=True):
        monitor.observe(_obs(signal_id, hit=hit, ic=ic))


# ──────────────────────────────────────────────────────────────────────────────
# 滚动窗指标与阈值判定（正常路径）
# ──────────────────────────────────────────────────────────────────────────────


class TestEvaluate:
    def test_healthy_none_no_alert(self) -> None:
        alerts: list = []
        m = _monitor(alerts)
        _feed(m, "sig-1", [True] * 5, [0.05] * 5)
        report = m.evaluate("sig-1")
        assert report.level is DegradationLevel.NONE
        assert not report.degraded
        assert report.reasons == ()
        assert report.sample_size == 5
        assert alerts == []
        assert not m.is_degraded("sig-1")
        assert m.weight_hint("sig-1") == 1.0

    def test_insufficient_samples_none(self) -> None:
        alerts: list = []
        m = _monitor(alerts)
        _feed(m, "sig-1", [False] * 3, [-0.5] * 3)  # 3 < min_samples 5
        report = m.evaluate("sig-1")
        assert report.level is DegradationLevel.NONE
        assert "样本不足" in report.reasons[0]
        assert alerts == []

    def test_hit_rate_below_floor_moderate(self) -> None:
        alerts: list = []
        marks: list = []
        m = _monitor(alerts, marks)
        _feed(m, "sig-1", [True, False, False, False, False], [0.05] * 5)  # 命中率 0.2
        report = m.evaluate("sig-1")
        assert report.level is DegradationLevel.MODERATE
        assert report.hit_rate == pytest.approx(0.2)
        assert any("命中率" in r for r in report.reasons)
        assert len(alerts) == 1
        assert marks == [("sig-1", DegradationLevel.MODERATE, 0.5)]
        assert m.weight_hint("sig-1") == 0.5

    def test_hit_rate_collapse_severe(self) -> None:
        m = _monitor()
        _feed(m, "sig-1", [False] * 5, [0.05] * 5)  # 命中率 0.0 < floor/2
        report = m.evaluate("sig-1")
        assert report.level is DegradationLevel.SEVERE
        assert any("崩塌" in r for r in report.reasons)

    def test_ic_below_floor_moderate(self) -> None:
        m = _monitor()
        _feed(m, "sig-1", [True] * 5, [0.01] * 5)  # IC 均值 0.01 < 0.02
        report = m.evaluate("sig-1")
        assert report.level is DegradationLevel.MODERATE
        assert any("IC" in r for r in report.reasons)

    def test_ic_sign_flip_severe(self) -> None:
        m = _monitor()
        _feed(m, "sig-1", [True] * 5, [-0.05] * 5)  # IC 均值 ≤ 0
        report = m.evaluate("sig-1")
        assert report.level is DegradationLevel.SEVERE

    def test_decay_mild(self) -> None:
        m = _monitor(window_size=6, min_samples=4)
        # 前半 0.2 → 后半 0.08，衰减 0.6 ∈ [0.5, 0.8)
        _feed(m, "sig-1", [True] * 4, [0.2, 0.2, 0.08, 0.08])
        report = m.evaluate("sig-1")
        assert report.level is DegradationLevel.MILD
        assert report.decay == pytest.approx(0.6)
        assert any("衰减" in r for r in report.reasons)

    def test_decay_moderate(self) -> None:
        m = _monitor(window_size=6, min_samples=4)
        # 前半 0.2 → 后半 0.02，衰减 0.9 ≥ 0.8
        _feed(m, "sig-1", [True] * 4, [0.2, 0.2, 0.02, 0.02])
        report = m.evaluate("sig-1")
        assert report.level is DegradationLevel.MODERATE
        assert report.decay == pytest.approx(0.9)

    def test_worst_of_composition(self) -> None:
        m = _monitor(window_size=6, min_samples=4)
        # 命中率崩塌(SEVERE) + IC 衰减(MILD) → SEVER
        _feed(m, "sig-1", [False] * 4, [0.2, 0.2, 0.08, 0.08])
        report = m.evaluate("sig-1")
        assert report.level is DegradationLevel.SEVERE
        assert len(report.reasons) == 2

    def test_degraded_evaluate_not_blocking(self) -> None:
        m = _monitor()
        _feed(m, "sig-1", [False] * 5, [-0.05] * 5)
        report = m.evaluate("sig-1")  # 降级不抛，返回报告
        assert report.degraded
        assert report.assessed_at == _T0

    def test_rolling_window_bounded(self) -> None:
        m = _monitor(window_size=4, min_samples=2)
        _feed(m, "sig-1", [True] * 6, [0.05] * 6)  # 6 条挤入 maxlen=4 窗
        report = m.evaluate("sig-1")
        assert report.sample_size == 4
        assert report.level is DegradationLevel.NONE


# ──────────────────────────────────────────────────────────────────────────────
# 告警与降权标记联动
# ──────────────────────────────────────────────────────────────────────────────


class TestAlertAndMark:
    def test_alert_payload(self) -> None:
        alerts: list = []
        m = _monitor(alerts)
        _feed(m, "sig-1", [False] * 5, [0.05] * 5)
        report = m.evaluate("sig-1")
        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.signal_id == "sig-1"
        assert alert.level is DegradationLevel.SEVERE
        assert alert.reasons == report.reasons
        assert alert.raised_at == _T0

    def test_alert_router_failure_not_blocking(self) -> None:
        def _bad_router(_alert) -> None:
            raise RuntimeError("告警通道故障")

        m = SignalDegradationMonitor(clock=lambda: _T0, alert_router=_bad_router)
        _feed(m, "sig-1", [False] * 5, [0.05] * 5)
        report = m.evaluate("sig-1")  # 告警失败不阻断
        assert report.level is DegradationLevel.SEVERE
        assert m.is_degraded("sig-1")

    def test_mark_once_per_level_alert_every_time(self) -> None:
        alerts: list = []
        marks: list = []
        m = _monitor(alerts, marks)
        _feed(m, "sig-1", [False] * 5, [0.05] * 5)
        m.evaluate("sig-1")
        m.evaluate("sig-1")  # 同级复评：告警再发，标记不重复
        assert len(alerts) == 2
        assert len(marks) == 1

    def test_recovery_clears_mark(self) -> None:
        marks: list = []
        m = _monitor(marks=marks, window_size=4, min_samples=2)
        _feed(m, "sig-1", [False] * 4, [-0.05] * 4)
        assert m.evaluate("sig-1").level is DegradationLevel.SEVERE
        assert m.is_degraded("sig-1")
        _feed(m, "sig-1", [True] * 4, [0.05] * 4)  # 好观测挤出旧窗
        report = m.evaluate("sig-1")
        assert report.level is DegradationLevel.NONE
        assert not m.is_degraded("sig-1")
        assert m.weight_hint("sig-1") == 1.0
        assert marks[-1] == ("sig-1", DegradationLevel.NONE, 1.0)

    def test_mark_sink_failure_not_blocking(self) -> None:
        def _bad_mark(_s, _lv, _w) -> None:
            raise RuntimeError("标记通道故障")

        m = SignalDegradationMonitor(clock=lambda: _T0, mark_sink=_bad_mark)
        _feed(m, "sig-1", [False] * 5, [0.05] * 5)
        report = m.evaluate("sig-1")
        assert report.degraded
        assert m.is_degraded("sig-1")  # 内存标记仍生效

    def test_marked_signals_sorted(self) -> None:
        m = _monitor()
        _feed(m, "sig-b", [False] * 5, [0.05] * 5)
        _feed(m, "sig-a", [False] * 5, [0.05] * 5)
        m.evaluate("sig-b")
        m.evaluate("sig-a")
        assert m.marked_signals() == ["sig-a", "sig-b"]


# ──────────────────────────────────────────────────────────────────────────────
# Fail-Closed 分支与确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestFailClosed:
    def test_unknown_signal_evaluate_raises(self) -> None:
        with pytest.raises(SignalDegradationError):
            _monitor().evaluate("ghost")

    def test_empty_signal_id_raises(self) -> None:
        m = _monitor()
        with pytest.raises(SignalDegradationError):
            m.observe(_obs(""))
        with pytest.raises(SignalDegradationError):
            m.evaluate("")

    def test_ic_out_of_range_raises(self) -> None:
        m = _monitor()
        with pytest.raises(SignalDegradationError):
            m.observe(_obs("sig-1", ic=1.1))
        with pytest.raises(SignalDegradationError):
            m.observe(_obs("sig-1", ic=-1.1))

    def test_hit_non_bool_raises(self) -> None:
        m = _monitor()
        with pytest.raises(SignalDegradationError):
            m.observe(_obs("sig-1", hit=1))  # type: ignore[arg-type]

    def test_invalid_constructor_params_raise(self) -> None:
        with pytest.raises(SignalDegradationError):
            _monitor(window_size=1)
        with pytest.raises(SignalDegradationError):
            _monitor(min_samples=0)
        with pytest.raises(SignalDegradationError):
            _monitor(window_size=6, min_samples=7)
        with pytest.raises(SignalDegradationError):
            _monitor(hit_rate_floor=0.0)
        with pytest.raises(SignalDegradationError):
            _monitor(ic_floor=0.0)
        with pytest.raises(SignalDegradationError):
            _monitor(decay_warn=0.9, decay_severe=0.8)
        with pytest.raises(SignalDegradationError):
            _monitor(degraded_weight=1.0)

    def test_deterministic_replay(self) -> None:
        hits = [True, False, False, True, False]
        ics = [0.2, 0.2, 0.08, 0.08, 0.05]
        m1, m2 = _monitor(), _monitor()
        _feed(m1, "sig-1", hits, ics)
        _feed(m2, "sig-1", hits, ics)
        r1, r2 = m1.evaluate("sig-1"), m2.evaluate("sig-1")
        assert (r1.level, r1.reasons) == (r2.level, r2.reasons)
        assert r1.hit_rate == r2.hit_rate
        assert r1.ic_mean == r2.ic_mean
        assert r1.decay == r2.decay
