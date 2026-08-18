# [BLUEPRINT] MOD-RK-18 | docs/03_modules/_domain_risk/model_risk_audit/blueprint.md | §test
# [MODULE] tests.risk.core.test_model_risk_audit
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.core.model_risk_audit
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_model_risk_audit.py
# [A_test] module_id: MOD-RK-18 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""G5 单元测试: ModelRiskAuditor — 漂移检测 + IC 衰减综合审计。

覆盖: risk_level 双维度矩阵、IC 衰减百分比/半衰期、bias 判定、
RiskCheckResult 转换、检测器异常 best-effort、幂等键。
"""

from __future__ import annotations

from decimal import Decimal

import pytest

pytest.importorskip(
    "zephyr.risk.core.model_risk_audit",
    reason="model_risk_audit not importable",
)

from zephyr.intelligence.model_drift_detector import DriftResult  # noqa: E402
from zephyr.risk.core.model_risk_audit import (  # noqa: E402
    DEFAULT_IC_DECAY_THRESHOLD,
    ModelRiskAuditor,
    ModelRiskAuditReport,
)

# ── Mock 漂移检测器（可控 drift_detected / divergence_score）─────────


class _MockDriftDetector:
    """可控的 ModelDriftDetector 替身，避免文件 I/O。"""

    def __init__(self, drift_detected: bool, divergence_score: float):
        self._drift_detected = drift_detected
        self._divergence_score = divergence_score

    def detect_drift(self, outputs):
        return DriftResult(
            drift_detected=self._drift_detected,
            model_name="test",
            divergence_score=self._divergence_score,
            threshold=0.15,
            exit_code=34 if self._drift_detected else 0,
            details=["mock"],
        )


class _FailingDriftDetector:
    """总是抛异常的检测器（测试 best-effort）。"""

    def detect_drift(self, outputs):
        raise RuntimeError("detector broken")


def _make_auditor(drift: bool = False, divergence: float = 0.0) -> ModelRiskAuditor:
    """创建注入 mock 检测器的审计器。"""
    return ModelRiskAuditor(drift_detector=_MockDriftDetector(drift, divergence))


# ── 无数据场景 ───────────────────────────────────────────────────────


class TestNoData:
    def test_no_data_low_risk(self):
        """无 model_outputs + 无 ic_data → low。"""
        auditor = _make_auditor()
        r = auditor.audit()
        assert r.drift_detected is False
        assert r.ic_decay_pct == 0.0
        assert r.risk_level == "low"
        assert r.is_breached is False if hasattr(r, "is_breached") else True

    def test_no_data_passed(self):
        auditor = _make_auditor()
        r = auditor.audit()
        check = auditor.to_risk_check_result(r)
        assert check.passed is True
        assert check.severity == "info"


# ── risk_level 矩阵 ─────────────────────────────────────────────────


class TestRiskLevelMatrix:
    """drift + ic_decay 双维度 → low/medium/high/critical。"""

    def test_no_drift_low_decay_low(self):
        """无 drift + ic_decay < 0.3 → low。"""
        auditor = _make_auditor(drift=False)
        r = auditor.audit(ic_data={1: 0.05, 5: 0.045, 10: 0.04})
        # decay = (0.05-0.04)/0.05 = 0.2 < 0.3
        assert r.ic_decay_pct == pytest.approx(0.2, abs=0.01)
        assert r.risk_level == "low"

    def test_no_drift_medium_decay_low(self):
        """无 drift + 0.3<=ic_decay<0.5 → low。"""
        auditor = _make_auditor(drift=False)
        r = auditor.audit(ic_data={1: 0.10, 5: 0.06})
        # decay = (0.10-0.06)/0.10 = 0.4
        assert r.ic_decay_pct == pytest.approx(0.4, abs=0.01)
        assert r.risk_level == "low"

    def test_no_drift_high_decay_medium(self):
        """无 drift + 0.5<=ic_decay<0.7 → medium。"""
        auditor = _make_auditor(drift=False)
        r = auditor.audit(ic_data={1: 0.10, 5: 0.04})
        # decay = (0.10-0.04)/0.10 = 0.6
        assert r.ic_decay_pct == pytest.approx(0.6, abs=0.01)
        assert r.risk_level == "medium"

    def test_no_drift_severe_decay_high(self):
        """无 drift + ic_decay>=0.7 → high。"""
        auditor = _make_auditor(drift=False)
        r = auditor.audit(ic_data={1: 0.10, 5: 0.02})
        # decay = (0.10-0.02)/0.10 = 0.8
        assert r.ic_decay_pct == pytest.approx(0.8, abs=0.01)
        assert r.risk_level == "high"

    def test_drift_low_decay_medium(self):
        """drift + ic_decay<0.3 → medium。"""
        auditor = _make_auditor(drift=True, divergence=0.20)
        r = auditor.audit(
            model_outputs=[{"pred": 1}],
            ic_data={1: 0.05, 5: 0.045, 10: 0.04},
        )
        assert r.drift_detected is True
        assert r.ic_decay_pct == pytest.approx(0.2, abs=0.01)
        assert r.risk_level == "medium"

    def test_drift_high_decay_high(self):
        """drift + 0.5<=ic_decay<0.7 → high。"""
        auditor = _make_auditor(drift=True, divergence=0.20)
        r = auditor.audit(
            model_outputs=[{"pred": 1}],
            ic_data={1: 0.10, 5: 0.04},
        )
        assert r.drift_detected is True
        assert r.risk_level == "high"

    def test_drift_severe_decay_critical(self):
        """drift + ic_decay>=0.7 → critical。"""
        auditor = _make_auditor(drift=True, divergence=0.20)
        r = auditor.audit(
            model_outputs=[{"pred": 1}],
            ic_data={1: 0.10, 5: 0.02},
        )
        assert r.drift_detected is True
        assert r.ic_decay_pct == pytest.approx(0.8, abs=0.01)
        assert r.risk_level == "critical"


# ── IC 半衰期 ────────────────────────────────────────────────────────


class TestIcHalfLife:
    def test_half_life_linear_interpolation(self):
        """IC 从 0.05(lag1) 衰减到 0.01(lag20)，半衰期=8.75。"""
        auditor = _make_auditor()
        r = auditor.audit(ic_data={1: 0.05, 5: 0.04, 10: 0.02, 20: 0.01})
        # half of 0.05 = 0.025; between lag5(0.04) and lag10(0.02)
        # ratio = (0.04-0.025)/(0.04-0.02) = 0.75 → 5 + 0.75*5 = 8.75
        assert r.ic_half_life == pytest.approx(8.75, abs=0.01)

    def test_no_ic_data_half_life_zero(self):
        auditor = _make_auditor()
        r = auditor.audit()
        assert r.ic_half_life == 0.0

    def test_zero_initial_ic_decay_zero(self):
        """initial_ic=0 → ic_decay_pct=0.0（避免除零）。"""
        auditor = _make_auditor()
        r = auditor.audit(ic_data={1: 0.0, 5: 0.0})
        assert r.ic_decay_pct == 0.0


# ── bias 判定 ────────────────────────────────────────────────────────


class TestBiasDetection:
    def test_bias_defaults_to_drift(self):
        """无显式 bias_score → bias_detected = drift_detected。"""
        auditor = _make_auditor(drift=True, divergence=0.20)
        r = auditor.audit(model_outputs=[{"pred": 1}])
        assert r.bias_detected is True

        auditor2 = _make_auditor(drift=False)
        r2 = auditor2.audit()
        assert r2.bias_detected is False

    def test_explicit_bias_score(self):
        """显式 bias_score > threshold → bias_detected=True。"""
        auditor = _make_auditor(drift=False)
        r = auditor.audit(bias_score=0.20)  # > 0.15 threshold
        assert r.bias_detected is True

    def test_explicit_bias_below_threshold(self):
        auditor = _make_auditor(drift=True, divergence=0.20)
        r = auditor.audit(model_outputs=[{"pred": 1}], bias_score=0.05)
        assert r.bias_detected is False  # explicit 0.05 < 0.15


# ── RiskCheckResult 转换 ─────────────────────────────────────────────


class TestToRiskCheckResult:
    def test_low_info_passed(self):
        auditor = _make_auditor(drift=False)
        r = auditor.audit()
        check = auditor.to_risk_check_result(r)
        assert check.passed is True
        assert check.severity == "info"

    def test_medium_warning(self):
        auditor = _make_auditor(drift=False)
        r = auditor.audit(ic_data={1: 0.10, 5: 0.04})  # 0.6 decay → medium
        check = auditor.to_risk_check_result(r)
        assert check.passed is False
        assert check.severity == "warning"

    def test_high_halt(self):
        auditor = _make_auditor(drift=False)
        r = auditor.audit(ic_data={1: 0.10, 5: 0.02})  # 0.8 decay → high
        check = auditor.to_risk_check_result(r)
        assert check.passed is False
        assert check.severity == "HALT"

    def test_critical_halt(self):
        auditor = _make_auditor(drift=True, divergence=0.20)
        r = auditor.audit(
            model_outputs=[{"pred": 1}],
            ic_data={1: 0.10, 5: 0.02},  # 0.8 decay → critical
        )
        check = auditor.to_risk_check_result(r)
        assert check.passed is False
        assert check.severity == "HALT"

    def test_rule_name(self):
        auditor = _make_auditor()
        r = auditor.audit()
        check = auditor.to_risk_check_result(r)
        assert check.rule_name == "model_risk_audit"

    def test_limit_value_is_drift_threshold(self):
        auditor = _make_auditor()
        r = auditor.audit()
        check = auditor.to_risk_check_result(r)
        assert check.limit_value == Decimal("0.15")


# ── best-effort 异常 ─────────────────────────────────────────────────


class TestBestEffort:
    def test_drift_detector_exception_no_crash(self):
        """检测器抛异常 → drift=False（降级），不崩溃。"""
        auditor = ModelRiskAuditor(drift_detector=_FailingDriftDetector())
        r = auditor.audit(model_outputs=[{"pred": 1}])
        assert r.drift_detected is False
        assert r.divergence_score == 0.0
        assert "error" in r.details["drift"]


# ── 阈值参数 ─────────────────────────────────────────────────────────


class TestThresholds:
    def test_default_drift_threshold_from_source(self):
        """drift_threshold 默认取 ModelDriftDetector.DIVERGENCE_THRESHOLD=0.15。"""
        auditor = ModelRiskAuditor()
        assert auditor._drift_threshold == 0.15

    def test_default_ic_decay_threshold(self):
        auditor = ModelRiskAuditor()
        assert auditor._ic_decay_threshold == DEFAULT_IC_DECAY_THRESHOLD

    def test_custom_drift_threshold(self):
        auditor = ModelRiskAuditor(drift_threshold=0.30)
        assert auditor._drift_threshold == 0.30


# ── 幂等键 ───────────────────────────────────────────────────────────


class TestIdempotencyKey:
    def test_unique_keys(self):
        auditor = _make_auditor()
        r1 = auditor.audit()
        r2 = auditor.audit()
        assert r1.idempotency_key != r2.idempotency_key
        assert r1.idempotency_key.startswith("modelrisk-")

    def test_frozen_report(self):
        auditor = _make_auditor()
        r = auditor.audit()
        with pytest.raises(Exception):
            r.risk_level = "critical"  # type: ignore[misc]
