# [BLUEPRINT] MOD-MLS-001 | docs/03_modules/_domain_ml_serve/model_drift_monitor/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-MLS-001 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [MODULE] tests.ml_serve.test_model_drift_monitor
# [TESTS] src/zephyr/ml_serve/core/model_drift_monitor.py
"""MOD-MLS-001 单元测试：model_drift_monitor 推理域 MS-03 模型漂移监控。

蓝图验收（B4-06990/CAND-MLS-001，D-ML-SERVE §0/§1 MS-03）：
PSI/JS/性能衰减/IC衰减 四维度量已知答案 + 四维独立阈值 +
E-OP-02 ModelDriftDetected 事件生产（event_sink 注入，异常不阻断）+
确定性事件顺序 PSI→PERFORMANCE→JS→IC。全部内存构造分布样本，不触网。
"""

from __future__ import annotations

import datetime

import numpy as np
import pytest

pytest.importorskip(
    "zephyr.ml_serve.core.model_drift_monitor",
    reason="model_drift_monitor not importable",
)

from zephyr.ml_serve.core.model_drift_monitor import (  # noqa: E402
    DriftEvaluation,
    DriftSeverity,
    DriftThresholds,
    DriftType,
    E_OP_02,
    ModelDriftError,
    ModelDriftMonitor,
    js_divergence,
    psi,
)

_T0 = datetime.datetime(2026, 8, 25, 15, 0, 0)
_REF = np.linspace(-2.0, 2.0, 200)
_SAME = _REF.copy()
_SHIFTED = _REF + 3.0


def _monitor(
    events: list | None = None,
    thresholds: DriftThresholds | None = None,
) -> ModelDriftMonitor:
    sink = (lambda e: events.append(e)) if events is not None else None
    return ModelDriftMonitor(
        thresholds=thresholds or DriftThresholds(),
        clock=lambda: _T0,
        event_sink=sink,
    )


def _flat(model_id: str = "m-1"):
    """全维无漂移输入。"""
    return dict(
        feature_ref=_REF, feature_cur=_SAME,
        output_ref=_REF, output_cur=_SAME,
        perf_ref=1.0, perf_cur=1.0,
        ic_ref=0.08, ic_cur=0.08,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 度量已知答案
# ──────────────────────────────────────────────────────────────────────────────


class TestMetrics:
    def test_psi_identical_near_zero(self) -> None:
        assert psi(_REF, _SAME) == pytest.approx(0.0, abs=1e-6)

    def test_psi_shifted_large(self) -> None:
        assert psi(_REF, _SHIFTED) > 1.0

    def test_psi_invalid_raises(self) -> None:
        with pytest.raises(ModelDriftError):
            psi(np.array([]), _SAME)
        with pytest.raises(ModelDriftError):
            psi(_REF, np.array([1.0, float("nan")]))
        with pytest.raises(ModelDriftError):
            psi(_REF, _SAME, buckets=1)

    def test_js_identical_near_zero(self) -> None:
        assert js_divergence(_REF, _SAME) == pytest.approx(0.0, abs=1e-6)

    def test_js_bounded_symmetric(self) -> None:
        v = js_divergence(_REF, _SHIFTED)
        assert 0.0 < v <= np.log(2.0) + 1e-9
        assert js_divergence(_REF, _SHIFTED) == pytest.approx(
            js_divergence(_SHIFTED, _REF)
        )


# ──────────────────────────────────────────────────────────────────────────────
# 阈值校验
# ──────────────────────────────────────────────────────────────────────────────


class TestThresholds:
    def test_warn_must_below_critical(self) -> None:
        with pytest.raises(ModelDriftError):
            DriftThresholds(psi_warn=0.25, psi_critical=0.25)
        with pytest.raises(ModelDriftError):
            DriftThresholds(ic_warn=-0.1)

    def test_domain_doc_defaults(self) -> None:
        t = DriftThresholds()
        assert t.psi_warn == pytest.approx(0.15)
        assert t.psi_critical == pytest.approx(0.25)
        assert t.perf_warn == pytest.approx(0.05)
        assert t.ic_critical == pytest.approx(0.50)


# ──────────────────────────────────────────────────────────────────────────────
# evaluate：E-OP-02 事件生产
# ──────────────────────────────────────────────────────────────────────────────


class TestEvaluate:
    def test_no_breach_no_events(self) -> None:
        events: list = []
        mon = _monitor(events)
        ev = mon.evaluate("m-1", **_flat())
        assert isinstance(ev, DriftEvaluation)
        assert ev.events == ()
        assert set(ev.metric_values) == {"psi", "js", "performance", "ic"}
        assert events == []

    def test_psi_warn_event(self) -> None:
        events: list = []
        mon = _monitor(events)
        kw = _flat()
        kw["feature_cur"] = _REF + 0.35  # 中度平移 → psi≈0.219 越 warn 不越 critical
        ev = mon.evaluate("m-psi", **kw)
        assert len(ev.events) == 1
        e = ev.events[0]
        assert e.event_id == E_OP_02
        assert e.model_id == "m-psi"
        assert e.drift_type is DriftType.PSI
        assert e.severity is DriftSeverity.WARN
        assert e.threshold == pytest.approx(0.15)
        assert e.detected_at == _T0
        assert events == list(ev.events)  # sink 外发一致

    def test_psi_critical_event(self) -> None:
        events: list = []
        mon = _monitor(events)
        kw = _flat()
        kw["feature_cur"] = _SHIFTED
        ev = mon.evaluate("m-1", **kw)
        assert ev.events[0].severity is DriftSeverity.CRITICAL
        assert ev.events[0].threshold == pytest.approx(0.25)

    def test_performance_decay_event(self) -> None:
        events: list = []
        mon = _monitor(events)
        kw = _flat()
        kw["perf_cur"] = 0.80  # (1.0-0.8)/1.0=0.20 ≥ crit 0.10
        ev = mon.evaluate("m-1", **kw)
        types = [e.drift_type for e in ev.events]
        assert DriftType.PERFORMANCE in types
        perf_e = [e for e in ev.events if e.drift_type is DriftType.PERFORMANCE][0]
        assert perf_e.drift_score == pytest.approx(0.20)
        assert perf_e.severity is DriftSeverity.CRITICAL

    def test_event_order_deterministic(self) -> None:
        events: list = []
        mon = _monitor(events)
        kw = _flat()
        kw["feature_cur"] = _SHIFTED       # PSI crit
        kw["output_cur"] = _SHIFTED        # JS crit
        kw["perf_cur"] = 0.5               # PERFORMANCE crit
        kw["ic_cur"] = 0.01                # IC decay 0.875 crit
        ev = mon.evaluate("m-1", **kw)
        assert [e.drift_type for e in ev.events] == [
            DriftType.PSI, DriftType.PERFORMANCE, DriftType.JS, DriftType.IC,
        ]

    def test_sink_exception_not_blocking(self) -> None:
        def _bad_sink(e) -> None:
            raise RuntimeError("bus down")

        mon = ModelDriftMonitor(clock=lambda: _T0, event_sink=_bad_sink)
        kw = _flat()
        kw["feature_cur"] = _SHIFTED
        ev = mon.evaluate("m-1", **kw)  # 不抛
        assert len(ev.events) == 1

    def test_invalid_inputs_raise(self) -> None:
        mon = _monitor()
        with pytest.raises(ModelDriftError):
            mon.evaluate("", **_flat())
        with pytest.raises(ModelDriftError):
            mon.evaluate("m-1", **{**_flat(), "perf_ref": float("nan")})
        with pytest.raises(ModelDriftError):
            mon.evaluate("m-1", **{**_flat(), "feature_ref": np.array([])})

    def test_determinism(self) -> None:
        kw = _flat()
        kw["feature_cur"] = _SHIFTED
        e1 = _monitor().evaluate("m-1", **kw)
        e2 = _monitor().evaluate("m-1", **kw)
        assert e1 == e2
