# [BLUEPRINT] MOD-DATENG-003 | docs/03_modules/_domain_data_eng/quality_sla_breach_predictor/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-DATENG-003 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.data_eng.test_quality_sla_breach_predictor
# [TESTS] src/zephyr/data_eng/quality_sla_breach_predictor.py
"""MOD-DATENG-003 单元测试：quality_sla_breach_predictor 质量SLA违约预测器。

蓝图验收（B14-04723/CAND-DATENG-006，A9运维架构）：
历史达成率+消耗速率线性外推预测违约窗口 + burn-rate 分级
（healthy|elevated|critical|exhausted）+ 提前告警回调 + 处置窗口建议。
序列/时钟/告警全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.data_eng.quality_sla_breach_predictor",
    reason="quality_sla_breach_predictor not importable",
)

from zephyr.data_eng.quality_sla_breach_predictor import (  # noqa: E402
    BreachForecast,
    BurnRateLevel,
    QualitySlaBreachPredictor,
    QualitySlaPredictorError,
    SloPoint,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 0, 0)
_HOUR = datetime.timedelta(hours=1)


def _predictor(alerts: list | None = None, **kw) -> QualitySlaBreachPredictor:
    return QualitySlaBreachPredictor(
        clock=lambda: _T0 + 3 * _HOUR,
        alert_sink=(lambda f: alerts.append(f)) if alerts is not None else None,
        **kw,
    )


def _hourly(values: list[float]) -> list[SloPoint]:
    return [SloPoint(observed_at=_T0 + i * _HOUR, attainment=v) for i, v in enumerate(values)]


def _registered(pred: QualitySlaBreachPredictor, target: float = 0.99) -> str:
    pred.register_slo("freshness", target)
    return "freshness"


# ── 构造/注册 Fail-Closed ─────────────────────────────────────────────────


def test_init_rejects_bad_thresholds():
    with pytest.raises(QualitySlaPredictorError, match="elevated_threshold"):
        QualitySlaBreachPredictor(elevated_threshold=-1.0)
    with pytest.raises(QualitySlaPredictorError, match="critical_threshold"):
        QualitySlaBreachPredictor(elevated_threshold=2.0, critical_threshold=1.0)


def test_register_slo_rejects_empty_name():
    pred = _predictor()
    with pytest.raises(QualitySlaPredictorError, match="为空"):
        pred.register_slo("", 0.99)


def test_register_slo_rejects_bad_target():
    pred = _predictor()
    for bad in (0.0, 1.0, -0.5, 1.5):
        with pytest.raises(QualitySlaPredictorError, match="target"):
            pred.register_slo("s", bad)


def test_register_slo_rejects_duplicate():
    pred = _predictor()
    pred.register_slo("freshness", 0.99)
    with pytest.raises(QualitySlaPredictorError, match="重复注册"):
        pred.register_slo("freshness", 0.999)


# ── forecast 输入 Fail-Closed ─────────────────────────────────────────────


def test_forecast_unknown_slo_rejected():
    pred = _predictor()
    with pytest.raises(QualitySlaPredictorError, match="未知 SLO"):
        pred.forecast("nope", _hourly([1.0, 1.0]))


def test_forecast_requires_two_points():
    pred = _predictor()
    name = _registered(pred)
    with pytest.raises(QualitySlaPredictorError, match="观测点不足"):
        pred.forecast(name, _hourly([0.99]))


def test_forecast_rejects_attainment_out_of_range():
    pred = _predictor()
    name = _registered(pred)
    with pytest.raises(QualitySlaPredictorError, match="越界"):
        pred.forecast(name, _hourly([1.0, 1.2]))


def test_forecast_sorts_unordered_points_deterministically():
    pred = _predictor()
    name = _registered(pred)
    ordered = _hourly([1.0, 0.999, 0.998, 0.997])
    shuffled = [ordered[2], ordered[0], ordered[3], ordered[1]]
    a = pred.forecast(name, ordered)
    b = pred.forecast(name, shuffled)
    assert a == b


# ── burn-rate 分级 ────────────────────────────────────────────────────────


def test_healthy_when_attainment_high():
    pred = _predictor()
    name = _registered(pred)
    fc = pred.forecast(name, _hourly([1.0, 1.0, 1.0, 1.0]))
    assert fc.level is BurnRateLevel.HEALTHY
    assert fc.burn_rate == 0.0
    assert fc.predicted_breach_at is None
    assert fc.action_window is None


def test_elevated_when_burn_rate_above_one():
    pred = _predictor()
    name = _registered(pred)
    fc = pred.forecast(name, _hourly([1.0, 1.0, 1.0, 0.985]))
    assert fc.level is BurnRateLevel.ELEVATED
    assert fc.burn_rate == pytest.approx(1.5)


def test_critical_alerts_when_burn_rate_above_two():
    alerts: list = []
    pred = _predictor(alerts=alerts)
    name = _registered(pred)
    fc = pred.forecast(name, _hourly([1.0, 1.0, 1.0, 0.97]))
    assert fc.level is BurnRateLevel.CRITICAL
    assert fc.burn_rate == pytest.approx(3.0)
    assert [f.slo_name for f in alerts] == ["freshness"]


def test_exhausted_when_error_budget_spent():
    alerts: list = []
    pred = _predictor(alerts=alerts)
    name = _registered(pred)
    # 0.985 恒低于 target：4 点消耗 162s > 预算 108s
    fc = pred.forecast(name, _hourly([0.985, 0.985, 0.985, 0.985]))
    assert fc.level is BurnRateLevel.EXHAUSTED
    # 预算耗尽时刻线性插值：第 3 个观测点（x=7200s）
    assert fc.predicted_breach_at == _T0 + 2 * _HOUR
    assert len(alerts) == 1


def test_elevated_does_not_alert():
    alerts: list = []
    pred = _predictor(alerts=alerts)
    name = _registered(pred)
    pred.forecast(name, _hourly([1.0, 1.0, 1.0, 0.985]))
    assert alerts == []


def test_alert_sink_exception_does_not_break():
    pred = QualitySlaBreachPredictor(
        clock=lambda: _T0,
        alert_sink=lambda f: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    name = _registered(pred)
    fc = pred.forecast(name, _hourly([0.985, 0.985, 0.985, 0.985]))
    assert fc.level is BurnRateLevel.EXHAUSTED


# ── 违约时间窗预测与处置窗口 ──────────────────────────────────────────────


def test_trend_extrapolation_predicts_breach_window():
    pred = _predictor()
    name = _registered(pred)
    # 缓慢线性劣化 0.001/h：fitted(t*)=0.99 → t*=36000s（10h 后）
    fc = pred.forecast(name, _hourly([1.0, 0.999, 0.998, 0.997]))
    assert fc.level is BurnRateLevel.HEALTHY
    assert fc.predicted_breach_at == _T0 + 10 * _HOUR
    assert fc.action_window == (_T0 + 3 * _HOUR, _T0 + 10 * _HOUR)


def test_budget_consumption_predicts_breach_when_trend_flat():
    pred = _predictor()
    name = _registered(pred)
    # 阶梯下探：拟合 t* 已过末次观测，预算消耗率外推 → 末次+10800s
    fc = pred.forecast(name, _hourly([1.0, 0.995, 0.99, 0.985]))
    assert fc.level is BurnRateLevel.ELEVATED
    assert fc.predicted_breach_at == _T0 + 3 * _HOUR + datetime.timedelta(seconds=10800)


def test_action_window_starts_at_injected_clock():
    pred = _predictor()
    name = _registered(pred)
    fc = pred.forecast(name, _hourly([1.0, 0.999, 0.998, 0.997]))
    assert fc.action_window is not None
    assert fc.action_window[0] == _T0 + 3 * _HOUR


def test_forecast_detail_contains_key_metrics():
    pred = _predictor()
    name = _registered(pred)
    fc = pred.forecast(name, _hourly([1.0, 0.999, 0.998, 0.997]))
    assert "burn_rate=0.3000" in fc.detail
    assert "target=0.99" in fc.detail


def test_same_timestamp_points_no_crash():
    pred = _predictor()
    name = _registered(pred)
    pts = [SloPoint(observed_at=_T0, attainment=0.999) for _ in range(3)]
    fc = pred.forecast(name, pts)
    assert fc.level is BurnRateLevel.HEALTHY
    assert fc.predicted_breach_at is None


# ── 确定性 ────────────────────────────────────────────────────────────────


def test_same_input_same_output():
    def _run() -> BreachForecast:
        pred = _predictor()
        name = _registered(pred)
        return pred.forecast(name, _hourly([1.0, 0.995, 0.99, 0.985]))

    assert _run() == _run()
