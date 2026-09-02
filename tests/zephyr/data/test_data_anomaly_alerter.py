# [BLUEPRINT] MOD-DATENG-001 | docs/03_modules/_domain_data_eng/data_anomaly_alerter/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-DATENG-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.zephyr.data.test_data_anomaly_alerter
# [TESTS] src/zephyr/data_eng/data_anomaly_alerter.py
"""MOD-DATENG-001 单元测试：data_anomaly_alerter 数据异常告警器。

蓝图验收（B13-04267/CAND-DATENG-004，A3 §17.1）：
四路检测（跳变 z-score/缺失率/量价背离/跨源偏差）+ AL-P1~P4 分级 +
同源同因合并 + 维护窗口静默 + 质量门控事件 + alert_sink 注入路由。
全部内存构造输入，不触网不触库。
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
import pytest

pytest.importorskip(
    "zephyr.data_eng.data_anomaly_alerter",
    reason="data_anomaly_alerter not importable",
)

from zephyr.data_eng.data_anomaly_alerter import (  # noqa: E402
    AlertGrade,
    AnomalyKind,
    AnomalySignal,
    DataAnomalyAlerter,
    DataAnomalyAlerterError,
    MaintenanceWindow,
    detect_cross_source_deviation,
    detect_missing_rate,
    detect_price_jumps,
    detect_volume_price_divergence,
)

_NOW = datetime(2026, 8, 25, 12, 0, 0, tzinfo=timezone.utc)


# ──────────────────────────────────────────────────────────────────────────────
# 四路检测
# ──────────────────────────────────────────────────────────────────────────────


class TestDetectPriceJumps:
    def test_flat_series_no_signal(self) -> None:
        closes = np.full(40, 10.0)
        assert detect_price_jumps(closes, symbol="X") == []

    def test_spike_triggers_signal(self) -> None:
        rng = np.random.default_rng(7)
        closes = 10.0 * np.exp(np.cumsum(rng.normal(0, 0.005, 60)))
        closes[-1] = closes[-2] * 1.5  # 末日暴涨 50%
        signals = detect_price_jumps(closes, symbol="600519.SH", z_threshold=4.0)
        assert len(signals) == 1
        sig = signals[0]
        assert sig.kind == AnomalyKind.PRICE_JUMP
        assert sig.symbol == "600519.SH"
        assert sig.metric_value >= 4.0
        assert sig.threshold == 4.0

    def test_too_short_series_fail_closed(self) -> None:
        with pytest.raises(DataAnomalyAlerterError):
            detect_price_jumps(np.array([1.0, 2.0]), symbol="X")

    def test_invalid_threshold_fail_closed(self) -> None:
        with pytest.raises(DataAnomalyAlerterError):
            detect_price_jumps(np.full(40, 10.0), symbol="X", z_threshold=0.0)


class TestDetectMissingRate:
    def test_no_missing_no_signal(self) -> None:
        assert detect_missing_rate(expected=100, actual=100, symbol="X") == []

    def test_missing_above_warn_triggers(self) -> None:
        signals = detect_missing_rate(expected=100, actual=90, symbol="X")
        assert len(signals) == 1
        sig = signals[0]
        assert sig.kind == AnomalyKind.MISSING_RATE
        assert sig.metric_value == pytest.approx(0.10)
        assert sig.threshold == pytest.approx(0.05)

    def test_invalid_counts_fail_closed(self) -> None:
        with pytest.raises(DataAnomalyAlerterError):
            detect_missing_rate(expected=0, actual=0, symbol="X")
        with pytest.raises(DataAnomalyAlerterError):
            detect_missing_rate(expected=100, actual=120, symbol="X")


class TestDetectVolumePriceDivergence:
    def test_divergence_triggers(self) -> None:
        # 价涨量缩：价格单调升、成交量单调降 → 负相关
        closes = np.linspace(10.0, 12.0, 30)
        volumes = np.linspace(1_000_000.0, 500_000.0, 30)
        signals = detect_volume_price_divergence(closes, volumes, symbol="X")
        assert len(signals) == 1
        assert signals[0].kind == AnomalyKind.VOLUME_PRICE_DIVERGENCE
        assert signals[0].metric_value < 0.0

    def test_positive_corr_no_signal(self) -> None:
        closes = np.linspace(10.0, 12.0, 30)
        volumes = np.linspace(500_000.0, 1_000_000.0, 30)
        assert detect_volume_price_divergence(closes, volumes, symbol="X") == []

    def test_length_mismatch_fail_closed(self) -> None:
        with pytest.raises(DataAnomalyAlerterError):
            detect_volume_price_divergence(np.linspace(10.0, 12.0, 30), np.ones(20), symbol="X")


class TestDetectCrossSourceDeviation:
    def test_within_tolerance_no_signal(self) -> None:
        primary = np.array([10.0, 10.1, 10.2])
        secondary = np.array([10.001, 10.099, 10.198])
        assert detect_cross_source_deviation(primary, secondary, symbol="X", tolerance_bps=30.0) == []

    def test_beyond_tolerance_triggers(self) -> None:
        primary = np.array([10.0, 10.1, 10.2])
        secondary = np.array([10.0, 10.1, 10.26])  # 末日偏差约 58.8bps
        signals = detect_cross_source_deviation(primary, secondary, symbol="X", tolerance_bps=30.0)
        assert len(signals) == 1
        sig = signals[0]
        assert sig.kind == AnomalyKind.CROSS_SOURCE_DEVIATION
        assert sig.metric_value > 30.0
        assert sig.threshold == 30.0

    def test_length_mismatch_fail_closed(self) -> None:
        with pytest.raises(DataAnomalyAlerterError):
            detect_cross_source_deviation(np.ones(3), np.ones(4), symbol="X", tolerance_bps=30.0)


# ──────────────────────────────────────────────────────────────────────────────
# 分级 + 抑制 + 路由 + 质量门控
# ──────────────────────────────────────────────────────────────────────────────


def _signal(
    kind: AnomalyKind = AnomalyKind.PRICE_JUMP, value: float = 4.5, threshold: float = 4.0, symbol: str = "600519.SH"
) -> AnomalySignal:
    return AnomalySignal(
        kind=kind,
        symbol=symbol,
        metric_value=value,
        threshold=threshold,
        detail="t",
    )


class TestGrading:
    def test_grade_mapping_by_ratio(self) -> None:
        alerter = DataAnomalyAlerter(alert_sink=lambda *a, **k: True)
        cases = [
            (1.0, AlertGrade.P4),
            (1.5, AlertGrade.P4),
            (2.0, AlertGrade.P3),
            (4.9, AlertGrade.P3),
            (5.0, AlertGrade.P2),
            (9.9, AlertGrade.P2),
            (10.0, AlertGrade.P1),
            (50.0, AlertGrade.P1),
        ]
        for ratio, expected in cases:
            sig = _signal(value=ratio * 4.0, threshold=4.0)
            alerts, _ = alerter.evaluate([sig], now_utc=_NOW)
            assert alerts[0].grade == expected, f"ratio={ratio}"

    def test_below_threshold_rejected(self) -> None:
        alerter = DataAnomalyAlerter(alert_sink=lambda *a, **k: True)
        with pytest.raises(DataAnomalyAlerterError):
            alerter.evaluate([_signal(value=3.9, threshold=4.0)], now_utc=_NOW)


class TestSuppression:
    def test_same_source_same_cause_merged(self) -> None:
        calls: list[dict] = []

        def sink(task_id, error, level, source=None, extra=None) -> bool:
            calls.append({"task_id": task_id, "level": level})
            return True

        alerter = DataAnomalyAlerter(alert_sink=sink, merge_window_sec=3600)
        sig = _signal()
        alerts1, _ = alerter.evaluate([sig], now_utc=_NOW)
        alerts2, _ = alerter.evaluate([sig], now_utc=_NOW + timedelta(minutes=5))
        assert alerts1[0].merged_count == 1
        assert alerts2[0].merged_count == 2  # 同源同因合并，计数累加
        assert len(calls) == 1  # 第二次不重复路由

    def test_merge_window_expired_routes_again(self) -> None:
        calls: list[dict] = []
        alerter = DataAnomalyAlerter(
            alert_sink=lambda *a, **k: calls.append({"a": a}) or True,
            merge_window_sec=60,
        )
        sig = _signal()
        alerter.evaluate([sig], now_utc=_NOW)
        alerter.evaluate([sig], now_utc=_NOW + timedelta(minutes=5))
        assert len(calls) == 2

    def test_maintenance_window_silenced(self) -> None:
        calls: list[dict] = []
        window = MaintenanceWindow(
            start_utc=_NOW - timedelta(hours=1),
            end_utc=_NOW + timedelta(hours=1),
            reason="周末维护",
        )
        alerter = DataAnomalyAlerter(
            alert_sink=lambda *a, **k: calls.append({"a": a}) or True,
            maintenance_windows=(window,),
        )
        alerts, events = alerter.evaluate([_signal()], now_utc=_NOW)
        assert alerts[0].silenced is True
        assert calls == []  # 静默不路由
        assert len(events) == 1  # 质量门控事件仍留痕


class TestRoutingAndGateEvents:
    def test_route_levels_mapped(self) -> None:
        seen: list[str] = []

        def sink(task_id, error, level, source=None, extra=None) -> bool:
            seen.append(level)
            return True

        alerter = DataAnomalyAlerter(alert_sink=sink)
        base = dict(kind=AnomalyKind.MISSING_RATE, symbol="X", detail="t")
        alerter.evaluate(
            [
                AnomalySignal(metric_value=0.50, threshold=0.05, **base),  # ratio 10 → P1→CRITICAL
                AnomalySignal(metric_value=0.30, threshold=0.05, **base),  # ratio 6 → P2→ERROR
            ],
            now_utc=_NOW,
        )
        # 注：两条 dedup_key 相同（同 source/kind/symbol）→ 第二条被合并
        assert seen == ["CRITICAL"]

    def test_gate_event_shape(self) -> None:
        alerter = DataAnomalyAlerter(alert_sink=lambda *a, **k: True)
        _, events = alerter.evaluate([_signal()], now_utc=_NOW)
        assert len(events) == 1
        ev = events[0]
        assert ev.kind == AnomalyKind.PRICE_JUMP
        assert ev.severity == AlertGrade.P4.value
        assert ev.symbol == "600519.SH"
        assert ev.metric_value == pytest.approx(4.5)
        assert "price_jump" in ev.message

    def test_sink_exception_swallowed(self) -> None:
        def bad_sink(*a, **k):
            raise RuntimeError("channel down")

        alerter = DataAnomalyAlerter(alert_sink=bad_sink)
        alerts, events = alerter.evaluate([_signal()], now_utc=_NOW)
        assert len(alerts) == 1 and len(events) == 1  # 通道异常不阻断判定


class TestDetectAndEvaluate:
    def test_one_stop(self) -> None:
        rng = np.random.default_rng(3)
        closes = 10.0 * np.exp(np.cumsum(rng.normal(0, 0.005, 60)))
        closes[-1] = closes[-2] * 1.6
        volumes = np.full(60, 1_000_000.0)
        alerter = DataAnomalyAlerter(alert_sink=lambda *a, **k: True)
        alerts, events = alerter.detect_and_evaluate(
            closes=closes,
            volumes=volumes,
            expected=100,
            actual=80,
            symbol="600519.SH",
            source="tdx",
            now_utc=_NOW,
        )
        kinds = {a.signal.kind for a in alerts}
        assert AnomalyKind.PRICE_JUMP in kinds
        assert AnomalyKind.MISSING_RATE in kinds
        assert len(events) == len(alerts)

    def test_all_clean(self) -> None:
        rng = np.random.default_rng(11)
        closes = 10.0 * np.exp(np.cumsum(rng.normal(0, 0.005, 60)))
        volumes = np.full(60, 1_000_000.0)
        alerter = DataAnomalyAlerter(alert_sink=lambda *a, **k: True)
        alerts, events = alerter.detect_and_evaluate(
            closes=closes,
            volumes=volumes,
            expected=100,
            actual=100,
            symbol="X",
            source="s",
            now_utc=_NOW,
        )
        assert alerts == []
        assert events == []
