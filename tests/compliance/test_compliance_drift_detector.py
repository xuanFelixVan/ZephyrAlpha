# [BLUEPRINT] MOD-CMP-016 | docs/03_modules/_domain_compliance/compliance_drift_detector/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-CMP-016 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.compliance.test_compliance_drift_detector
# [TESTS] src/zephyr/compliance/compliance_drift_detector.py
"""MOD-CMP-016 单元测试：compliance_drift_detector 合规漂移检测器。

蓝图验收（B14-04656/CAND-CMP-007，canonical 承接 CMP-004，§0定位/§1规则）：
基线快照 diff（声明缺失/值漂移/未申报生效三类）+ AL-P3 告警 + 证据快照 +
整改任务生成 + 仅非交易时段运行（时段判定注入）。时钟/汇/时段全注入，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.compliance.compliance_drift_detector",
    reason="compliance_drift_detector not importable",
)

from zephyr.compliance.compliance_drift_detector import (  # noqa: E402
    AlertLevel,
    ComplianceDriftDetector,
    ComplianceDriftError,
    DriftAlert,
    DriftEvidence,
)

_T0 = datetime.datetime(2026, 8, 25, 20, 0, 0)

_BASELINE = {
    "r-cancel.cancel_rate_threshold": 0.5,
    "r-wash.self_trade_threshold": 0.3,
    "code_path.detector": "zephyr.compliance.trading_compliance_detector",
}


def _detector(
    non_trading: bool = True,
    alerts: list | None = None,
    evidences: list | None = None,
) -> ComplianceDriftDetector:
    return ComplianceDriftDetector(
        clock=lambda: _T0,
        alert_sink=(lambda a: alerts.append(a)) if alerts is not None else None,
        evidence_sink=(lambda e: evidences.append(e)) if evidences is not None else None,
        is_non_trading_time=lambda: non_trading,
    )


def _seeded(**kw) -> ComplianceDriftDetector:
    d = _detector(**kw)
    d.set_baseline(_BASELINE)
    return d


# ──────────────────────────────────────────────────────────────────────────────
# 基线登记
# ──────────────────────────────────────────────────────────────────────────────


class TestBaseline:
    def test_set_baseline_ok(self) -> None:
        _seeded()

    def test_empty_baseline_raises(self) -> None:
        d = _detector()
        with pytest.raises(ComplianceDriftError):
            d.set_baseline({})

    def test_non_mapping_raises(self) -> None:
        d = _detector()
        with pytest.raises(ComplianceDriftError):
            d.set_baseline([("k", 1)])

    def test_empty_key_raises(self) -> None:
        d = _detector()
        with pytest.raises(ComplianceDriftError):
            d.set_baseline({"": 1})


# ──────────────────────────────────────────────────────────────────────────────
# 时段门禁 + Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestGuards:
    def test_trading_time_raises(self) -> None:
        d = _seeded(non_trading=False)
        with pytest.raises(ComplianceDriftError):
            d.run_check(dict(_BASELINE))

    def test_no_baseline_raises(self) -> None:
        d = _detector()
        with pytest.raises(ComplianceDriftError):
            d.run_check(dict(_BASELINE))

    def test_provider_non_mapping_raises(self) -> None:
        d = _seeded()
        with pytest.raises(ComplianceDriftError):
            d.run_check(lambda: [1, 2, 3])

    def test_bad_current_key_raises(self) -> None:
        d = _seeded()
        with pytest.raises(ComplianceDriftError):
            d.run_check({"": 1})


# ──────────────────────────────────────────────────────────────────────────────
# diff 比对
# ──────────────────────────────────────────────────────────────────────────────


class TestDiff:
    def test_no_drift(self) -> None:
        d = _seeded()
        report = d.run_check(dict(_BASELINE))
        assert report.drifted is False
        assert report.items == ()
        assert report.tasks == ()

    def test_value_drift(self) -> None:
        d = _seeded()
        current = dict(_BASELINE)
        current["r-cancel.cancel_rate_threshold"] = 0.3
        report = d.run_check(current)
        assert report.drifted is True
        assert len(report.items) == 1
        item = report.items[0]
        assert item.key == "r-cancel.cancel_rate_threshold"
        assert item.declared == 0.5
        assert item.actual == 0.3

    def test_declared_missing(self) -> None:
        d = _seeded()
        current = dict(_BASELINE)
        del current["r-wash.self_trade_threshold"]
        report = d.run_check(current)
        assert report.items[0].actual == "<MISSING>"

    def test_undeclared_effective(self) -> None:
        d = _seeded()
        current = dict(_BASELINE)
        current["r-new.undeclared"] = 1
        report = d.run_check(current)
        assert report.items[0].key == "r-new.undeclared"
        assert report.items[0].declared == "<UNDECLARED>"

    def test_diff_sorted_by_key(self) -> None:
        d = _seeded()
        report = d.run_check({
            "z-undeclared": 9,
            "a-undeclared": 1,
        })
        assert [it.key for it in report.items] == [
            "a-undeclared",
            "code_path.detector",
            "r-cancel.cancel_rate_threshold",
            "r-wash.self_trade_threshold",
            "z-undeclared",
        ]

    def test_provider_callable(self) -> None:
        d = _seeded()
        report = d.run_check(lambda: dict(_BASELINE))
        assert report.drifted is False


# ──────────────────────────────────────────────────────────────────────────────
# 三联动：AL-P3 告警 + 证据快照 + 整改任务
# ──────────────────────────────────────────────────────────────────────────────


class TestTripleAction:
    def _drift(self, d: ComplianceDriftDetector):
        current = dict(_BASELINE)
        current["r-cancel.cancel_rate_threshold"] = 0.3
        current["rogue.param"] = True
        return d.run_check(current)

    def test_alert_al_p3(self) -> None:
        alerts: list[DriftAlert] = []
        d = _seeded(alerts=alerts)
        self._drift(d)
        assert len(alerts) == 1
        assert alerts[0].level is AlertLevel.AL_P3
        assert alerts[0].keys == ("r-cancel.cancel_rate_threshold", "rogue.param")

    def test_evidence_snapshot(self) -> None:
        evidences: list[DriftEvidence] = []
        d = _seeded(evidences=evidences)
        report = self._drift(d)
        assert len(evidences) == 1
        assert evidences[0].items == report.items  # 差异清单留证

    def test_remediation_tasks_generated(self) -> None:
        d = _seeded()
        report = self._drift(d)
        assert len(report.tasks) == 2
        t = report.tasks[0]
        assert t.key == "r-cancel.cancel_rate_threshold"
        assert "声明 0.5" in t.suggestion
        assert "生效 0.3" in t.suggestion
        assert d.remediation_tasks() == sorted(report.tasks, key=lambda x: x.task_id)

    def test_no_drift_no_side_effects(self) -> None:
        alerts: list[DriftAlert] = []
        evidences: list[DriftEvidence] = []
        d = _seeded(alerts=alerts, evidences=evidences)
        d.run_check(dict(_BASELINE))
        assert alerts == []
        assert evidences == []
        assert d.remediation_tasks() == []

    def test_task_id_monotonic_across_runs(self) -> None:
        d = _seeded()
        r1 = self._drift(d)
        r2 = self._drift(d)
        ids = [t.task_id for t in (*r1.tasks, *r2.tasks)]
        assert ids == sorted(ids)
        assert len(set(ids)) == len(ids)

    def test_alert_sink_failure_not_blocking(self) -> None:
        d = ComplianceDriftDetector(
            clock=lambda: _T0,
            alert_sink=lambda a: (_ for _ in ()).throw(RuntimeError("boom")),
            is_non_trading_time=lambda: True,
        )
        d.set_baseline(_BASELINE)
        report = self._drift(d)
        assert report.drifted is True  # 告警异常不阻断比对

    def test_deterministic_same_input(self) -> None:
        d1 = _seeded()
        d2 = _seeded()
        r1 = self._drift(d1)
        r2 = self._drift(d2)
        assert r1.items == r2.items
        assert [t.suggestion for t in r1.tasks] == [t.suggestion for t in r2.tasks]
