# [BLUEPRINT] MOD-AUDITTEST-001 | docs/03_modules/_domain_simulation/quality_assurance_selfdrive/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-AUDITTEST-001 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.simulation.test_quality_assurance_selfdrive
# [TESTS] src/zephyr/simulation/quality_assurance_selfdrive.py
"""MOD-AUDITTEST-001 单元测试：quality_assurance_selfdrive 质量保障自驱动器。

蓝图验收（B1-00346/CAND-AUDITTES-001，蓝图 §1规则/§2接口）：
①契约变更触发测试骨架自生成（schema→pytest骨架文本，注入writer，含TODO标记）
②look_ahead偏差自诊断接线（注入检测器回调，异常包装Fail-Closed）
③性能回归基线比对（退化>阈值告警）④数据准确率抽检（注入随机源+校验器，不达标告警）。
随机源/检测器/校验器/writer/告警全注入内存替身，不触网不落盘。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.simulation.quality_assurance_selfdrive",
    reason="quality_assurance_selfdrive not importable",
)

from zephyr.simulation.quality_assurance_selfdrive import (  # noqa: E402
    QualityAlert,
    QualityAssuranceSelfdrive,
    QualitySelfdriveError,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)

_SCHEMA = {"symbol": "str", "price": "float", "volume": "int"}


def _drive(
    alerts: list | None = None,
    *,
    rng=None,
    detector=None,
    writer=None,
) -> QualityAssuranceSelfdrive:
    return QualityAssuranceSelfdrive(
        clock=lambda: _T0,
        random_source=rng,
        bias_detector=detector,
        skeleton_writer=writer if writer is not None else (lambda n, t: None),
        alert_sink=(lambda a: alerts.append(a)) if alerts is not None else None,
    )


# ──────────────────────────────────────────────────────────────────────────────
# ① 契约变更触发测试骨架自生成
# ──────────────────────────────────────────────────────────────────────────────


class TestSkeletonGen:
    def test_generate_ok_and_deterministic(self) -> None:
        drive = _drive()
        skeleton = drive.generate_test_skeleton("bar_contract", _SCHEMA)
        assert skeleton.contract_name == "bar_contract"
        assert skeleton.fields == ("price", "symbol", "volume")  # 字段按名确定性排序
        assert skeleton.generated_at == _T0
        again = _drive().generate_test_skeleton("bar_contract", _SCHEMA)
        assert again.skeleton_text == skeleton.skeleton_text  # 同输入必同输出

    def test_skeleton_text_contains_todo_and_fields(self) -> None:
        drive = _drive()
        skeleton = drive.generate_test_skeleton("bar_contract", _SCHEMA)
        text = skeleton.skeleton_text
        assert "TODO" in text
        for field in ("price", "symbol", "volume"):
            assert f"test_bar_contract_has_field_{field}" in text

    def test_skeleton_delivered_via_writer(self) -> None:
        written: list[tuple[str, str]] = []
        drive = _drive(writer=lambda n, t: written.append((n, t)))
        skeleton = drive.generate_test_skeleton("bar_contract", _SCHEMA)
        assert written == [("bar_contract", skeleton.skeleton_text)]  # 仅经注入writer

    def test_invalid_contract_name_raises(self) -> None:
        with pytest.raises(QualitySelfdriveError):
            _drive().generate_test_skeleton("", _SCHEMA)
        with pytest.raises(QualitySelfdriveError):
            _drive().generate_test_skeleton("bad-name!", _SCHEMA)

    def test_invalid_schema_raises(self) -> None:
        with pytest.raises(QualitySelfdriveError):
            _drive().generate_test_skeleton("bar_contract", {})
        with pytest.raises(QualitySelfdriveError):
            _drive().generate_test_skeleton("bar_contract", {"not a field": "str"})

    def test_writer_not_injected_fail_closed(self) -> None:
        drive = QualityAssuranceSelfdrive(clock=lambda: _T0)
        with pytest.raises(QualitySelfdriveError):
            drive.generate_test_skeleton("bar_contract", _SCHEMA)


# ──────────────────────────────────────────────────────────────────────────────
# ② look_ahead 偏差自诊断接线
# ──────────────────────────────────────────────────────────────────────────────


class TestBiasDiagnose:
    def test_clean(self) -> None:
        drive = _drive(detector=lambda target: [])
        diag = drive.diagnose_bias("features_v3")
        assert diag.is_clean is True
        assert diag.issues == ()
        assert diag.diagnosed_at == _T0

    def test_issues_alerted(self) -> None:
        alerts: list[QualityAlert] = []
        drive = _drive(alerts, detector=lambda target: ["标签泄露: label 混入特征列"])
        diag = drive.diagnose_bias("features_v3")
        assert diag.is_clean is False
        assert len(alerts) == 1
        assert alerts[0].kind == "bias_detected"
        assert alerts[0].subject == "features_v3"

    def test_detector_not_injected_fail_closed(self) -> None:
        drive = QualityAssuranceSelfdrive(clock=lambda: _T0)
        with pytest.raises(QualitySelfdriveError):
            drive.diagnose_bias("features_v3")
        with pytest.raises(QualitySelfdriveError):
            _drive(detector=lambda target: []).diagnose_bias("")  # 空目标

    def test_detector_exception_wrapped(self) -> None:
        def _boom(target: str):
            raise RuntimeError("detector crash")

        drive = _drive(detector=_boom)
        with pytest.raises(QualitySelfdriveError):
            drive.diagnose_bias("features_v3")


# ──────────────────────────────────────────────────────────────────────────────
# ③ 性能回归基线比对
# ──────────────────────────────────────────────────────────────────────────────


class TestRegression:
    _BASE = {"sharpe": 2.0, "win_rate": 0.6}

    def test_no_degradation(self) -> None:
        alerts: list[QualityAlert] = []
        drive = _drive(alerts)
        report = drive.compare_performance({"sharpe": 2.1, "win_rate": 0.6}, self._BASE, threshold=0.1)
        assert report.degraded == ()
        assert alerts == []

    def test_degradation_alerted(self) -> None:
        alerts: list[QualityAlert] = []
        drive = _drive(alerts)
        report = drive.compare_performance({"sharpe": 1.5, "win_rate": 0.6}, self._BASE, threshold=0.1)
        assert report.degraded == ("sharpe",)  # 退化 (2.0-1.5)/2.0=0.25 > 0.1
        assert len(alerts) == 1
        assert alerts[0].kind == "performance_regression"
        assert abs(report.ratios["sharpe"] - 0.25) < 1e-9

    def test_boundary_not_alerted(self) -> None:
        alerts: list[QualityAlert] = []
        drive = _drive(alerts)
        report = drive.compare_performance({"sharpe": 1.8, "win_rate": 0.6}, self._BASE, threshold=0.1)
        assert report.degraded == ()  # 恰等于阈值不告警（须 > 阈值）
        assert alerts == []

    def test_missing_current_metric_raises(self) -> None:
        drive = _drive()
        with pytest.raises(QualitySelfdriveError):
            drive.compare_performance({"sharpe": 2.0}, self._BASE, threshold=0.1)

    def test_invalid_baseline_or_threshold_raises(self) -> None:
        with pytest.raises(QualitySelfdriveError):
            _drive().compare_performance({}, {}, threshold=0.1)  # 空基线
        with pytest.raises(QualitySelfdriveError):
            _drive().compare_performance({"sharpe": 2.0, "win_rate": 0.6}, self._BASE, threshold=-0.1)

    def test_zero_baseline_edge(self) -> None:
        drive = _drive()
        report = drive.compare_performance({"alpha": 0.0}, {"alpha": 0.0}, threshold=0.1)
        assert report.degraded == ()  # 基线 0 且当前 0 → 无退化
        report2 = drive.compare_performance({"alpha": -0.5}, {"alpha": 0.0}, threshold=0.1)
        assert report2.degraded == ("alpha",)


# ──────────────────────────────────────────────────────────────────────────────
# ④ 数据准确率抽检
# ──────────────────────────────────────────────────────────────────────────────


class _SeqRng:
    """确定性序列随机源（内存替身）。"""

    def __init__(self, values: list[float]) -> None:
        self._values = values
        self._i = 0

    def __call__(self) -> float:
        value = self._values[self._i % len(self._values)]
        self._i += 1
        return value


class TestAccuracy:
    _RECORDS = ["r0", "r1", "r2", "r3", "r4"]

    def _rng(self) -> _SeqRng:
        return _SeqRng([0.9, 0.1, 0.7, 0.3, 0.5])  # 确定性抽样序列

    def test_all_pass(self) -> None:
        alerts: list[QualityAlert] = []
        drive = _drive(alerts, rng=self._rng())
        report = drive.sample_accuracy(self._RECORDS, 3, lambda r: True, min_accuracy=0.8)
        assert report.sample_size == 3
        assert report.passed == 3
        assert report.accuracy == 1.0
        assert report.meets_standard is True
        assert alerts == []

    def test_below_standard_alerted(self) -> None:
        alerts: list[QualityAlert] = []
        drive = _drive(alerts, rng=self._rng())
        # 校验器仅认 "r0"/"r1" 合格；抽样必含不合格记录
        report = drive.sample_accuracy(self._RECORDS, 4, lambda r: r in {"r0", "r1"}, min_accuracy=0.9)
        assert report.meets_standard is False
        assert len(alerts) == 1
        assert alerts[0].kind == "accuracy_below_standard"

    def test_boundary_meets_standard(self) -> None:
        alerts: list[QualityAlert] = []
        drive = _drive(alerts, rng=self._rng())
        report = drive.sample_accuracy(self._RECORDS, 2, lambda r: True, min_accuracy=1.0)
        assert report.meets_standard is True  # 恰等于下限不告警
        assert alerts == []

    def test_deterministic_same_rng_sequence(self) -> None:
        d1 = _drive(rng=self._rng())
        d2 = _drive(rng=self._rng())
        validator = lambda r: r != "r3"  # noqa: E731
        r1 = d1.sample_accuracy(self._RECORDS, 4, validator, min_accuracy=0.5)
        r2 = d2.sample_accuracy(self._RECORDS, 4, validator, min_accuracy=0.5)
        assert (r1.passed, r1.accuracy) == (r2.passed, r2.accuracy)  # 同输入必同输出

    def test_invalid_records_or_sample_size_raises(self) -> None:
        drive = _drive(rng=self._rng())
        with pytest.raises(QualitySelfdriveError):
            drive.sample_accuracy([], 1, lambda r: True, min_accuracy=0.8)
        with pytest.raises(QualitySelfdriveError):
            drive.sample_accuracy(self._RECORDS, 0, lambda r: True, min_accuracy=0.8)
        with pytest.raises(QualitySelfdriveError):
            drive.sample_accuracy(self._RECORDS, 6, lambda r: True, min_accuracy=0.8)

    def test_validator_not_injected_fail_closed(self) -> None:
        drive = _drive(rng=self._rng())
        with pytest.raises(QualitySelfdriveError):
            drive.sample_accuracy(self._RECORDS, 2, None, min_accuracy=0.8)

    def test_validator_exception_wrapped(self) -> None:
        def _boom(record):
            raise ValueError("bad record")

        drive = _drive(rng=self._rng())
        with pytest.raises(QualitySelfdriveError):
            drive.sample_accuracy(self._RECORDS, 2, _boom, min_accuracy=0.8)

    def test_random_source_fail_closed(self) -> None:
        drive = QualityAssuranceSelfdrive(clock=lambda: _T0)
        with pytest.raises(QualitySelfdriveError):
            drive.sample_accuracy(self._RECORDS, 2, lambda r: True, min_accuracy=0.8)
        bad = _drive(rng=_SeqRng([1.5]))
        with pytest.raises(QualitySelfdriveError):
            bad.sample_accuracy(self._RECORDS, 2, lambda r: True, min_accuracy=0.8)
