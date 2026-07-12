# [A_test] module_id: SRC-TST-1502 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_safety_brake
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] test_safety_brake.py
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from zephyr.gov_kb.safety_brake import (
    OperationType,
    PreFlightResult,
    RiskLevel,
    SafetyBrake,
)


class TestSafetyBrake:
    def _make_brake(self, tmp_path: Path) -> SafetyBrake:
        return SafetyBrake(project_root=tmp_path)

    def test_pre_flight_low_risk(self, tmp_path: Path):
        sb = self._make_brake(tmp_path)
        result = sb.pre_flight_check(OperationType.WRITE, affected_ke_count=1)
        assert isinstance(result, PreFlightResult)
        assert result.passed is True
        assert result.risk_level == RiskLevel.LOW

    def test_pre_flight_delete_medium(self, tmp_path: Path):
        sb = self._make_brake(tmp_path)
        result = sb.pre_flight_check(OperationType.DELETE, affected_ke_count=3)
        assert result.risk_level == RiskLevel.MEDIUM

    def test_pre_flight_delete_high(self, tmp_path: Path):
        sb = self._make_brake(tmp_path)
        result = sb.pre_flight_check(OperationType.DELETE, affected_ke_count=15)
        assert result.risk_level == RiskLevel.HIGH
        assert result.cooling_period_seconds > 0

    def test_pre_flight_purge_critical(self, tmp_path: Path):
        sb = self._make_brake(tmp_path)
        result = sb.pre_flight_check(OperationType.PURGE)
        assert result.risk_level == RiskLevel.CRITICAL
        assert result.devils_advocate_required is True
        assert result.cooling_period_seconds > 0

    def test_pre_flight_epidemic_blocked(self, tmp_path: Path):
        sb = self._make_brake(tmp_path)
        result = sb.pre_flight_check(OperationType.BATCH_UPDATE, affected_ke_count=100)
        assert result.passed is False
        assert len(result.blocking_issues) > 0

    def test_pre_flight_mark_authoritative(self, tmp_path: Path):
        sb = self._make_brake(tmp_path)
        result = sb.pre_flight_check(OperationType.MARK_AUTHORITATIVE)
        assert result.risk_level == RiskLevel.HIGH
        assert result.devils_advocate_required is True
        assert any("Devil" in w for w in result.warnings)

    def test_pre_flight_purge_warning(self, tmp_path: Path):
        sb = self._make_brake(tmp_path)
        result = sb.pre_flight_check(OperationType.PURGE)
        assert any("Irreversible" in w for w in result.warnings)

    def test_pre_flight_delete_many_warning(self, tmp_path: Path):
        sb = self._make_brake(tmp_path)
        result = sb.pre_flight_check(OperationType.DELETE, affected_ke_count=10)
        assert any("tombstone" in w.lower() for w in result.warnings)

    def test_pre_flight_skip_cooling(self, tmp_path: Path):
        sb = self._make_brake(tmp_path)
        result = sb.pre_flight_check(OperationType.DELETE, affected_ke_count=15, skip_cooling=True)
        assert result.cooling_period_seconds == 0

    def test_pre_flight_reclassify_low(self, tmp_path: Path):
        sb = self._make_brake(tmp_path)
        result = sb.pre_flight_check(OperationType.RECLASSIFY, affected_ke_count=1)
        assert result.risk_level == RiskLevel.LOW

    def test_pre_flight_reclassify_medium(self, tmp_path: Path):
        sb = self._make_brake(tmp_path)
        result = sb.pre_flight_check(OperationType.RECLASSIFY, affected_ke_count=15)
        assert result.risk_level == RiskLevel.MEDIUM

    def test_pre_flight_batch_update_levels(self, tmp_path: Path):
        sb = self._make_brake(tmp_path)
        r1 = sb.pre_flight_check(OperationType.BATCH_UPDATE, affected_ke_count=3)
        assert r1.risk_level == RiskLevel.LOW
        r2 = sb.pre_flight_check(OperationType.BATCH_UPDATE, affected_ke_count=10)
        assert r2.risk_level == RiskLevel.MEDIUM
        r3 = sb.pre_flight_check(OperationType.BATCH_UPDATE, affected_ke_count=25)
        assert r3.risk_level == RiskLevel.HIGH


class TestDevilsAdvocate:
    def _make_brake(self, tmp_path: Path) -> SafetyBrake:
        return SafetyBrake(project_root=tmp_path)

    def test_accepted(self, tmp_path: Path):
        sb = self._make_brake(tmp_path)
        result = sb.devils_advocate(
            "claim",
            evidence_for=["a", "b"],
            evidence_against=["c"],
        )
        assert result["verdict"] == "accepted"
        assert result["for_count"] == 2
        assert result["against_count"] == 1

    def test_rejected(self, tmp_path: Path):
        sb = self._make_brake(tmp_path)
        result = sb.devils_advocate(
            "claim",
            evidence_for=["a"],
            evidence_against=["b", "c", "d"],
        )
        assert result["verdict"] == "rejected"

    def test_tied(self, tmp_path: Path):
        sb = self._make_brake(tmp_path)
        result = sb.devils_advocate(
            "claim",
            evidence_for=["a"],
            evidence_against=["b"],
        )
        assert result["verdict"] == "tied"

    def test_insufficient_evidence(self, tmp_path: Path):
        sb = self._make_brake(tmp_path)
        result = sb.devils_advocate("claim")
        assert result["verdict"] == "insufficient_evidence"

    def test_none_evidence(self, tmp_path: Path):
        sb = self._make_brake(tmp_path)
        result = sb.devils_advocate("claim", evidence_for=None, evidence_against=None)
        assert result["verdict"] == "insufficient_evidence"

    def test_result_has_claim_and_timestamp(self, tmp_path: Path):
        sb = self._make_brake(tmp_path)
        result = sb.devils_advocate("test claim")
        assert result["claim"] == "test claim"
        assert "timestamp" in result


class TestCoolingPeriod:
    def test_immediate_return(self, tmp_path: Path):
        sb = SafetyBrake(project_root=tmp_path)
        with patch("zephyr.knowledge.kb.safety_brake.time.sleep", return_value=None):
            result = sb.cooling_period(seconds=0, reason="test")
            assert result is True

    def test_keyboard_interrupt(self, tmp_path: Path):
        sb = SafetyBrake(project_root=tmp_path)
        with patch("zephyr.knowledge.kb.safety_brake.time.sleep", side_effect=KeyboardInterrupt):
            result = sb.cooling_period(seconds=5, reason="test")
            assert result is False


class TestPreFlightResult:
    def test_defaults(self):
        r = PreFlightResult(
            operation="write",
            risk_level=RiskLevel.LOW,
            affected_ke_count=1,
            cooling_period_seconds=0,
            passed=True,
        )
        assert r.blocking_issues == []
        assert r.warnings == []

    def test_custom_issues(self):
        r = PreFlightResult(
            operation="delete",
            risk_level=RiskLevel.HIGH,
            affected_ke_count=10,
            cooling_period_seconds=30,
            passed=False,
            blocking_issues=["issue1"],
            warnings=["warn1"],
        )
        assert len(r.blocking_issues) == 1
        assert len(r.warnings) == 1


class TestEnums:
    def test_risk_levels(self):
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.CRITICAL.value == "critical"

    def test_operation_types(self):
        assert OperationType.WRITE.value == "write"
        assert OperationType.PURGE.value == "purge"
