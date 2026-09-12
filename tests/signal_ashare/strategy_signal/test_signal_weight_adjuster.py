# [BLUEPRINT] MOD-SIG-131 | docs/03_modules/_domain_signal/signal_weight_adjuster/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIG-131 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.signal_ashare.test_signal_weight_adjuster
# [TESTS] src/zephyr/signal_ashare/signal_weight_adjuster.py
"""MOD-SIG-131 单元测试：signal_weight_adjuster 信号权重调节器。

蓝图验收（B11-02593/CAND-TESTB-054，A7 技能signal-weight-adjust）：
滚动IC/胜率/回撤三指标加权得分→目标权重 + 单次调整限幅20% +
权重变更审计回调 + 按版本回滚 + 漂移告警。
审计/告警全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.signal_ashare.signal_weight_adjuster",
    reason="signal_weight_adjuster not importable",
)

from zephyr.signal_ashare.signal_weight_adjuster import (  # noqa: E402
    MetricSample,
    RollingMetrics,
    SignalWeightAdjuster,
    SignalWeightConfig,
    SignalWeightError,
    WeightChangeRecord,
    WeightDriftAlert,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)


def _adjuster(
    audits: list | None = None,
    alerts: list | None = None,
    **cfg_kwargs,
) -> SignalWeightAdjuster:
    return SignalWeightAdjuster(
        config=SignalWeightConfig(**cfg_kwargs),
        clock=lambda: _T0,
        audit_sink=(lambda r: audits.append(r)) if audits is not None else None,
        alert_sink=(lambda a: alerts.append(a)) if alerts is not None else None,
    )


def _good(adj: SignalWeightAdjuster, sid: str = "s1", n: int = 3) -> None:
    """录入 n 条优质样本（高IC/高胜率/零回撤）。"""
    for _ in range(n):
        adj.record_metrics(sid, ic=0.5, win_rate=0.8, drawdown=0.0)


# ----------------------------------------------------------------------
# 注册 / 指标录入 Fail-Closed
# ----------------------------------------------------------------------
def test_register_ok() -> None:
    adj = _adjuster()
    adj.register_signal("s1", 0.5)
    assert adj.current_weight("s1") == pytest.approx(0.5)
    assert adj.version_of("s1") == 1
    assert adj.history("s1") == ((1, 0.5),)


def test_register_duplicate_rejected() -> None:
    adj = _adjuster()
    adj.register_signal("s1", 0.5)
    with pytest.raises(SignalWeightError):
        adj.register_signal("s1", 0.6)


def test_register_empty_id_rejected() -> None:
    adj = _adjuster()
    with pytest.raises(SignalWeightError):
        adj.register_signal("  ", 0.5)


def test_register_nonpositive_weight_rejected() -> None:
    adj = _adjuster()
    with pytest.raises(SignalWeightError):
        adj.register_signal("s1", 0.0)
    with pytest.raises(SignalWeightError):
        adj.register_signal("s2", -0.1)


def test_record_metrics_unregistered_rejected() -> None:
    adj = _adjuster()
    with pytest.raises(SignalWeightError):
        adj.record_metrics("ghost", ic=0.1, win_rate=0.5, drawdown=0.1)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"ic": 1.5, "win_rate": 0.5, "drawdown": 0.1},
        {"ic": 0.1, "win_rate": -0.1, "drawdown": 0.1},
        {"ic": 0.1, "win_rate": 0.5, "drawdown": 1.1},
        {"ic": float("nan"), "win_rate": 0.5, "drawdown": 0.1},
    ],
)
def test_record_metrics_out_of_range_rejected(kwargs) -> None:
    adj = _adjuster()
    adj.register_signal("s1", 0.5)
    with pytest.raises(SignalWeightError):
        adj.record_metrics("s1", **kwargs)


def test_rolling_metrics_empty_rejected() -> None:
    adj = _adjuster()
    adj.register_signal("s1", 0.5)
    with pytest.raises(SignalWeightError):
        adj.rolling_metrics("s1")


def test_config_invalid_rejected() -> None:
    with pytest.raises(SignalWeightError):
        SignalWeightConfig(window=0)
    with pytest.raises(SignalWeightError):
        SignalWeightConfig(ic_coef=0.0, win_coef=0.0, dd_coef=0.0)
    with pytest.raises(SignalWeightError):
        SignalWeightConfig(min_weight=1.0, max_weight=0.5)
    with pytest.raises(SignalWeightError):
        SignalWeightConfig(adjust_cap=0.0)


# ----------------------------------------------------------------------
# 滚动窗口 / 得分 / 目标权重
# ----------------------------------------------------------------------
def test_rolling_window_trims_oldest() -> None:
    adj = _adjuster(window=3)
    adj.register_signal("s1", 0.5)
    adj.record_metrics("s1", ic=0.9, win_rate=0.9, drawdown=0.0)
    for _ in range(3):
        adj.record_metrics("s1", ic=-0.5, win_rate=0.2, drawdown=0.5)
    m = adj.rolling_metrics("s1")
    assert isinstance(m, RollingMetrics)
    assert m.samples == 3
    assert m.mean_ic == pytest.approx(-0.5)
    assert m.mean_win_rate == pytest.approx(0.2)
    assert m.max_drawdown == pytest.approx(0.5)


def test_score_perfect_metrics_target_max() -> None:
    adj = _adjuster()
    adj.register_signal("s1", 0.5)
    adj.record_metrics("s1", ic=1.0, win_rate=1.0, drawdown=0.0)
    assert adj.score("s1") == pytest.approx(1.0)
    assert adj.target_weight("s1") == pytest.approx(1.0)


def test_score_worst_metrics_target_min() -> None:
    adj = _adjuster()
    adj.register_signal("s1", 0.5)
    adj.record_metrics("s1", ic=-1.0, win_rate=0.0, drawdown=1.0)
    assert adj.score("s1") == pytest.approx(0.0)
    assert adj.target_weight("s1") == pytest.approx(0.0)


def test_target_weight_respects_min_max() -> None:
    adj = _adjuster(min_weight=0.1, max_weight=0.6)
    adj.register_signal("s1", 0.3)
    adj.record_metrics("s1", ic=1.0, win_rate=1.0, drawdown=0.0)
    assert adj.target_weight("s1") == pytest.approx(0.6)
    adj2 = _adjuster(min_weight=0.1, max_weight=0.6)
    adj2.register_signal("s1", 0.3)
    adj2.record_metrics("s1", ic=-1.0, win_rate=0.0, drawdown=1.0)
    assert adj2.target_weight("s1") == pytest.approx(0.1)


# ----------------------------------------------------------------------
# 调整限幅 / 审计
# ----------------------------------------------------------------------
def test_adjust_up_capped_at_20pct() -> None:
    audits: list = []
    adj = _adjuster(audits=audits)
    adj.register_signal("s1", 0.2)
    adj.record_metrics("s1", ic=1.0, win_rate=1.0, drawdown=0.0)
    rec = adj.adjust("s1", reason="t")
    assert isinstance(rec, WeightChangeRecord)
    assert rec.capped is True
    assert rec.new_weight == pytest.approx(0.24)  # 0.2 * 1.2
    assert rec.version == 2
    assert rec.changed_at == _T0
    assert audits == [rec]


def test_adjust_down_capped_at_20pct() -> None:
    adj = _adjuster()
    adj.register_signal("s1", 0.8)
    adj.record_metrics("s1", ic=-1.0, win_rate=0.0, drawdown=1.0)
    rec = adj.adjust("s1")
    assert rec.capped is True
    assert rec.new_weight == pytest.approx(0.64)  # 0.8 * 0.8


def test_adjust_uncapped_when_delta_small() -> None:
    adj = _adjuster()
    adj.register_signal("s1", 0.8)  # 距目标0.82仅0.02 < 限幅0.16
    _good(adj, "s1")
    target = adj.target_weight("s1")
    rec = adj.adjust("s1")
    assert rec.capped is False
    assert rec.new_weight == pytest.approx(target)
    assert adj.version_of("s1") == 2


def test_adjust_unregistered_rejected() -> None:
    adj = _adjuster()
    with pytest.raises(SignalWeightError):
        adj.adjust("ghost")


def test_adjust_without_samples_rejected() -> None:
    adj = _adjuster()
    adj.register_signal("s1", 0.5)
    with pytest.raises(SignalWeightError):
        adj.adjust("s1")


def test_adjust_versions_increment_and_history() -> None:
    adj = _adjuster()
    adj.register_signal("s1", 0.2)
    _good(adj, "s1")
    adj.adjust("s1")
    adj.adjust("s1")
    assert adj.version_of("s1") == 3
    versions = [v for v, _ in adj.history("s1")]
    assert versions == [1, 2, 3]


# ----------------------------------------------------------------------
# 回滚
# ----------------------------------------------------------------------
def test_rollback_restores_weight_as_new_version() -> None:
    audits: list = []
    adj = _adjuster(audits=audits)
    adj.register_signal("s1", 0.2)
    _good(adj, "s1")
    adj.adjust("s1")
    assert adj.current_weight("s1") == pytest.approx(0.24)
    rec = adj.rollback("s1", 1)
    assert rec.new_weight == pytest.approx(0.2)
    assert adj.current_weight("s1") == pytest.approx(0.2)
    assert adj.version_of("s1") == 3
    assert rec.reason == "rollback"
    assert audits[-1] is rec


def test_rollback_unknown_version_rejected() -> None:
    adj = _adjuster()
    adj.register_signal("s1", 0.2)
    with pytest.raises(SignalWeightError):
        adj.rollback("s1", 99)
    with pytest.raises(SignalWeightError):
        adj.rollback("s1", 0)


def test_rollback_unregistered_rejected() -> None:
    adj = _adjuster()
    with pytest.raises(SignalWeightError):
        adj.rollback("ghost", 1)


# ----------------------------------------------------------------------
# 漂移告警
# ----------------------------------------------------------------------
def test_drift_alert_fires_when_deviation_exceeds_threshold() -> None:
    alerts: list = []
    adj = _adjuster(alerts=alerts, drift_threshold=0.1)
    adj.register_signal("s1", 0.2)
    adj.record_metrics("s1", ic=1.0, win_rate=1.0, drawdown=0.0)
    result = adj.check_drift()
    assert len(result) == 1
    alert = result[0]
    assert isinstance(alert, WeightDriftAlert)
    assert alert.signal_id == "s1"
    assert alert.deviation > 0.1
    assert alert.at == _T0
    assert alerts == [alert]


def test_drift_no_alert_within_threshold() -> None:
    alerts: list = []
    adj = _adjuster(alerts=alerts, drift_threshold=0.7)
    adj.register_signal("s1", 0.5)
    _good(adj, "s1")  # 目标0.82 偏差0.64 < 阈值0.7
    assert adj.check_drift() == ()
    assert alerts == []


def test_drift_skips_signals_without_samples() -> None:
    adj = _adjuster()
    adj.register_signal("s1", 0.5)
    assert adj.check_drift() == ()


def test_drift_multiple_signals_sorted() -> None:
    adj = _adjuster(drift_threshold=0.05)
    adj.register_signal("b_sig", 0.2)
    adj.register_signal("a_sig", 0.2)
    for sid in ("a_sig", "b_sig"):
        adj.record_metrics(sid, ic=1.0, win_rate=1.0, drawdown=0.0)
    result = adj.check_drift()
    assert [a.signal_id for a in result] == ["a_sig", "b_sig"]


# ----------------------------------------------------------------------
# 确定性
# ----------------------------------------------------------------------
def test_determinism_same_ops_same_result() -> None:
    def run() -> tuple:
        adj = _adjuster()
        adj.register_signal("s1", 0.2)
        for ic, wr, dd in ((0.3, 0.6, 0.1), (0.4, 0.7, 0.05), (0.2, 0.5, 0.2)):
            adj.record_metrics("s1", ic=ic, win_rate=wr, drawdown=dd)
        r1 = adj.adjust("s1")
        r2 = adj.adjust("s1")
        return (r1.new_weight, r2.new_weight, adj.version_of("s1"))

    assert run() == run()
