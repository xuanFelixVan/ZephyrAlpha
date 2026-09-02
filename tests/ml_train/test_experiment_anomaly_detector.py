# [BLUEPRINT] MOD-ML-023 | docs/03_modules/_domain_machine_learning_train/experiment_anomaly_detector/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-ML-023 | layer=test | stability=volatile | safety=L | ai_autonomy=human_gated
# [MODULE] tests.ml_train.test_experiment_anomaly_detector
# [TESTS] src/zephyr/ml_train/experiment_anomaly_detector.py
"""MOD-ML-023 单元测试：experiment_anomaly_detector 实验指标异常检测。

合成序列已知答案验证（纯内存，不触网）：
- 正常序列（缓慢改进+小幅振荡）三类检测器均不误报；
- 突变（rolling z-score）warn/critical 分档命中；
- 漂移（CUSUM 双侧）上/下两个方向各命中且越阈复位；
- 停滞（连续 N 次改进 < epsilon）warn 与 2N critical 各报一次；
- 非有限值（nan，loss 爆炸形态）记 critical 突变且不进统计窗；
- 配置非法 Fail-Closed（ZA-MLT-0015）。
"""

from __future__ import annotations

import pytest

from zephyr.ml_train.experiment_anomaly_detector import (
    ANOMALY_DRIFT,
    ANOMALY_SPIKE,
    ANOMALY_STAGNATION,
    SEVERITY_CRITICAL,
    SEVERITY_WARN,
    AnomalyDetectionConfig,
    MetricAnomalyReport,
    ExperimentAnomalyError,
    ExperimentMetricPoint,
    detect_experiment_anomalies,
)

_EXP = "exp-001"
_METRIC = "ic"


def _points(values: list[float], experiment_id: str = _EXP, metric: str = _METRIC) -> list[ExperimentMetricPoint]:
    return [
        ExperimentMetricPoint(experiment_id=experiment_id, metric_name=metric, value=v, ts=i)
        for i, v in enumerate(values)
    ]


def _normal_series(n: int = 60) -> list[float]:
    """正常序列：缓慢改进 + 周期小幅振荡（三类检测器均应静默）。

    每 4 步一个小峰（逐峰抬升 0.0002 >= eps，避免停滞）；基线带均值零漂移
    （避免 CUSUM 累积）；峰/谷偏离历史窗均值均在 3σ 内（避免突变）。
    """
    out = []
    for i in range(n):
        base = 0.5 + (0.001 if i % 2 else -0.001)
        if i % 4 == 0:
            base = 0.502 + 0.0002 * (i // 4)
        out.append(base)
    return out


def test_normal_series_no_false_positive() -> None:
    """正常序列：60 点零异常报告。"""
    reports = detect_experiment_anomalies(_points(_normal_series()))
    assert reports == []


def test_spike_warn_and_critical() -> None:
    """突变：+3.5σ 记 warn、+8σ 记 critical（其余检测器隔离关闭）。"""
    cfg = AnomalyDetectionConfig(cusum_h=100.0, stagnation_n=100, min_warmup=5)
    base = [0.5 + (0.001 if i % 2 else -0.001) for i in range(20)]
    warn_series = base + [0.5035]  # z=+3.5 -> warn
    crit_series = base + [0.508]  # z=+8 -> critical
    points = _points(warn_series, experiment_id="exp-warn") + _points(crit_series, experiment_id="exp-crit")
    reports = detect_experiment_anomalies(points, cfg)

    spikes = [r for r in reports if r.anomaly_type == ANOMALY_SPIKE]
    assert len(spikes) == 2
    by_exp = {r.experiment_id: r for r in spikes}
    assert by_exp["exp-warn"].severity == SEVERITY_WARN
    assert by_exp["exp-warn"].evidence["z_score"] == pytest.approx(3.5, rel=1e-6)
    assert by_exp["exp-crit"].severity == SEVERITY_CRITICAL
    assert by_exp["exp-crit"].evidence["z_score"] == pytest.approx(8.0, rel=1e-6)
    assert by_exp["exp-warn"].ts == 20


def test_drift_up_and_down_via_cusum() -> None:
    """漂移：基线恒定振荡后单侧 +1σ/-1σ 持续偏移，CUSUM 双侧各命中两次（越阈复位）。"""
    cfg = AnomalyDetectionConfig(z_warn=100.0, z_critical=200.0, cusum_h=2.0, stagnation_n=100, min_warmup=5)
    base = [0.5 + (0.001 if i % 2 else -0.001) for i in range(20)]  # mu=0.5 sigma=0.001
    up_series = base + [0.501] * 10  # z=+1.0/步 -> s_pos 每步+0.5，第5步 2.5>2.0 出报复位
    down_series = base + [0.499] * 10
    points = _points(up_series, metric="sharpe") + _points(down_series, metric="loss")
    reports = detect_experiment_anomalies(points, cfg)

    drifts = [r for r in reports if r.anomaly_type == ANOMALY_DRIFT]
    up = [r for r in drifts if r.metric_name == "sharpe"]
    down = [r for r in drifts if r.metric_name == "loss"]
    assert len(up) == 2 and len(down) == 2
    assert {r.evidence["direction"] for r in up} == {"up"}
    assert {r.evidence["direction"] for r in down} == {"down"}
    assert {r.severity for r in drifts} == {SEVERITY_WARN}  # 2.5 < 2*h=4 -> warn
    assert up[0].evidence["cusum_stat"] == pytest.approx(2.5, rel=1e-9)
    assert up[0].ts == 24  # 基线 20 点 + 漂移第 5 点


def test_stagnation_warn_then_critical() -> None:
    """停滞：连续 5 次改进 < eps 记 warn，达 10 次升 critical，各报一次。"""
    cfg = AnomalyDetectionConfig(z_warn=100.0, z_critical=200.0, cusum_h=100.0, stagnation_n=5, stagnation_eps=1e-3)
    values = [0.50, 0.51, 0.52, 0.53, 0.54] + [0.54] * 12
    reports = detect_experiment_anomalies(_points(values), cfg)

    stagn = [r for r in reports if r.anomaly_type == ANOMALY_STAGNATION]
    assert len(stagn) == 2
    assert stagn[0].severity == SEVERITY_WARN
    assert stagn[0].evidence["run_length"] == 5
    assert stagn[0].ts == 9
    assert stagn[1].severity == SEVERITY_CRITICAL
    assert stagn[1].evidence["run_length"] == 10
    assert stagn[1].ts == 14
    assert stagn[0].evidence["best"] == pytest.approx(0.54)


def test_stagnation_lower_is_better_direction() -> None:
    """指标方向：higher_is_better=False（loss 口径）下停滞同样命中。"""
    cfg = AnomalyDetectionConfig(
        z_warn=100.0, z_critical=200.0, cusum_h=100.0, stagnation_n=5, stagnation_eps=1e-3, higher_is_better=False
    )
    values = [0.50, 0.49, 0.48] + [0.48] * 6  # loss 降到 0.48 后停滞
    reports = detect_experiment_anomalies(_points(values), cfg)
    stagn = [r for r in reports if r.anomaly_type == ANOMALY_STAGNATION]
    assert len(stagn) == 1
    assert stagn[0].severity == SEVERITY_WARN
    assert stagn[0].evidence["best"] == pytest.approx(0.48)


def test_non_finite_value_critical_spike_and_excluded() -> None:
    """非有限值：nan 记 critical 突变且不进统计窗（后续正常点不受污染）。"""
    cfg = AnomalyDetectionConfig(cusum_h=100.0, stagnation_n=100, min_warmup=5)
    base = [0.5 + (0.001 if i % 2 else -0.001) for i in range(10)]
    values = base + [float("nan"), 0.5005]
    reports = detect_experiment_anomalies(_points(values), cfg)
    assert len(reports) == 1
    rep = reports[0]
    assert rep.anomaly_type == ANOMALY_SPIKE
    assert rep.severity == SEVERITY_CRITICAL
    assert rep.ts == 10
    assert rep.evidence["reason"] == "non_finite_value"


def test_multi_experiment_grouping_isolated() -> None:
    """分组隔离：异常只归属所在 (experiment_id, metric_name) 序列。"""
    cfg = AnomalyDetectionConfig(cusum_h=100.0, stagnation_n=100, min_warmup=5)
    base = [0.5 + (0.001 if i % 2 else -0.001) for i in range(20)]
    points = _points(base + [0.508], experiment_id="exp-bad") + _points(base, experiment_id="exp-good")
    reports = detect_experiment_anomalies(points, cfg)
    assert {r.experiment_id for r in reports} == {"exp-bad"}


def test_empty_input_returns_empty() -> None:
    assert detect_experiment_anomalies([]) == []


def test_determinism_same_input_same_output() -> None:
    """同输入必同输出（含证据值逐位一致）。"""
    cfg = AnomalyDetectionConfig(cusum_h=2.0, stagnation_n=5, stagnation_eps=1e-3)
    values = [0.50, 0.51, 0.52, 0.53, 0.54] + [0.54] * 12 + [0.60]
    points = _points(values)
    first = detect_experiment_anomalies(points, cfg)
    second = detect_experiment_anomalies(points, cfg)
    assert first == second
    assert all(isinstance(r, MetricAnomalyReport) for r in first)


def test_invalid_config_fail_closed() -> None:
    """配置非法 Fail-Closed（错误码 ZA-MLT-0015）。"""
    points = _points(_normal_series(10))
    with pytest.raises(ExperimentAnomalyError) as exc_info:
        detect_experiment_anomalies(points, AnomalyDetectionConfig(z_window=1))
    assert exc_info.value.error_code == "ZA-MLT-0015"
    with pytest.raises(ExperimentAnomalyError):
        detect_experiment_anomalies(points, AnomalyDetectionConfig(z_warn=0.0))
    with pytest.raises(ExperimentAnomalyError):
        detect_experiment_anomalies(points, AnomalyDetectionConfig(z_warn=5.0, z_critical=3.0))
    with pytest.raises(ExperimentAnomalyError):
        detect_experiment_anomalies(points, AnomalyDetectionConfig(cusum_k=0.0))
    with pytest.raises(ExperimentAnomalyError):
        detect_experiment_anomalies(points, AnomalyDetectionConfig(stagnation_n=0))
    with pytest.raises(ExperimentAnomalyError):
        detect_experiment_anomalies(points, AnomalyDetectionConfig(stagnation_eps=-1e-3))
    with pytest.raises(ExperimentAnomalyError):
        detect_experiment_anomalies(points, AnomalyDetectionConfig(min_warmup=99))
