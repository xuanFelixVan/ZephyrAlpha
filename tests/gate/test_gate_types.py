# [A_test] module_id: SRC-TST-1047 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3.2

# [MODULE] tests.test_gate_types

# [INVARIANTS] GateViolation fields immutable after creation; GateResult.passed is bool; GateViolationError.result is GateResult

# [MODIFY-GUARD] none

# [CONSUMERS] pytest

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] GateViolationError raised only with GateResult; GateEngineError is RuntimeError subclass

# [TESTS] tests/test_gate_types.py
# [TTL] task_bound

from __future__ import annotations

from datetime import datetime

import pytest

from zephyr.gov_enforcement.rule_enforcement.gate_types import (
    GateEngineError,
    GateResult,
    GateViolation,
    GateViolationError,
)
from zephyr.integration.shared.schema.schemas import Priority


class TestGateViolation:
    def test_creation_with_required_fields(self):
        v = GateViolation(check_id="CHK-001", check_name="encoding", severity="P0", message="bad encoding")
        assert v.check_id == "CHK-001"
        assert v.check_name == "encoding"
        assert v.severity == "P0"
        assert v.message == "bad encoding"
        assert v.detail is None

    def test_creation_with_detail(self):
        v = GateViolation(
            check_id="CHK-002", check_name="path", severity="P1", message="invalid path", detail="/bad/path"
        )
        assert v.detail == "/bad/path"

    def test_empty_strings(self):
        v = GateViolation(check_id="", check_name="", severity="", message="")
        assert v.check_id == ""
        assert v.detail is None

    def test_severity_values(self):
        for sev in ("P0", "P1", "P2", "P3", "P4"):
            v = GateViolation(check_id="X", check_name="X", severity=sev, message="X")
            assert v.severity == sev


class TestGateResult:
    def test_passed_result_defaults(self):
        r = GateResult(gate_id="G1", task_id="T-001", passed=True)
        assert r.gate_id == "G1"
        assert r.task_id == "T-001"
        assert r.passed is True
        assert r.violations == []
        assert r.details == {}
        assert r.evaluated_at

    def test_failed_result_with_violations(self):
        v1 = GateViolation(check_id="C1", check_name="a", severity="P0", message="fail")
        v2 = GateViolation(check_id="C2", check_name="b", severity="P1", message="warn")
        r = GateResult(gate_id="G2", task_id="T-002", passed=False, violations=[v1, v2], details={"score": 0.3})
        assert r.passed is False
        assert len(r.violations) == 2
        assert r.details == {"score": 0.3}

    def test_p0_violations_filters_correctly(self):
        v0 = GateViolation(check_id="C0", check_name="x", severity=Priority.P0.value, message="critical")
        v1 = GateViolation(check_id="C1", check_name="y", severity=Priority.P1.value, message="minor")
        r = GateResult(gate_id="G3", task_id="T-003", passed=False, violations=[v0, v1])
        p0 = r.p0_violations
        assert len(p0) == 1
        assert p0[0].check_id == "C0"

    def test_p0_violations_empty_when_none(self):
        r = GateResult(gate_id="G4", task_id="T-004", passed=True)
        assert r.p0_violations == []

    def test_has_p0_true(self):
        v = GateViolation(check_id="C", check_name="z", severity=Priority.P0.value, message="p0")
        r = GateResult(gate_id="G5", task_id="T-005", passed=False, violations=[v])
        assert r.has_p0 is True

    def test_has_p0_false(self):
        v = GateViolation(check_id="C", check_name="z", severity=Priority.P2.value, message="p2")
        r = GateResult(gate_id="G6", task_id="T-006", passed=False, violations=[v])
        assert r.has_p0 is False

    def test_has_p0_false_when_passed(self):
        r = GateResult(gate_id="G7", task_id="T-007", passed=True)
        assert r.has_p0 is False

    def test_summary_passed(self):
        r = GateResult(gate_id="G1", task_id="T-100", passed=True)
        s = r.summary()
        assert "[PASS]" in s
        assert "G1" in s
        assert "T-100" in s

    def test_summary_failed(self):
        v0 = GateViolation(check_id="C0", check_name="a", severity=Priority.P0.value, message="critical")
        v1 = GateViolation(check_id="C1", check_name="b", severity=Priority.P1.value, message="minor")
        r = GateResult(gate_id="G2", task_id="T-200", passed=False, violations=[v0, v1])
        s = r.summary()
        assert "[FAIL]" in s
        assert "G2" in s
        assert "T-200" in s
        assert "violations=2" in s
        assert "P0=1" in s

    def test_summary_failed_zero_p0(self):
        v = GateViolation(check_id="C", check_name="a", severity=Priority.P2.value, message="low")
        r = GateResult(gate_id="G3", task_id="T-300", passed=False, violations=[v])
        s = r.summary()
        assert "P0=0" in s

    def test_evaluated_at_is_iso_format(self):
        r = GateResult(gate_id="G8", task_id="T-008", passed=True)
        parsed = datetime.fromisoformat(r.evaluated_at)
        assert parsed.tzinfo is not None

    def test_empty_violations_and_details(self):
        r = GateResult(gate_id="G9", task_id="T-009", passed=True, violations=[], details={})
        assert r.violations == []
        assert r.details == {}

    def test_details_with_various_types(self):
        r = GateResult(
            gate_id="G10",
            task_id="T-010",
            passed=False,
            details={"list_val": [1, 2], "nested": {"a": 1}, "none_val": None, "bool_val": False},
        )
        assert r.details["list_val"] == [1, 2]
        assert r.details["nested"]["a"] == 1
        assert r.details["none_val"] is None
        assert r.details["bool_val"] is False


class TestGateEngineError:
    def test_is_runtime_error(self):
        assert issubclass(GateEngineError, RuntimeError)

    def test_instantiation(self):
        err = GateEngineError("engine failure")
        assert str(err) == "engine failure"

    def test_instantiation_no_args(self):
        err = GateEngineError()
        assert isinstance(err, RuntimeError)


class TestGateViolationError:
    def test_is_gate_engine_error(self):
        assert issubclass(GateViolationError, GateEngineError)

    def test_is_runtime_error(self):
        assert issubclass(GateViolationError, RuntimeError)

    def test_stores_result(self):
        r = GateResult(gate_id="G1", task_id="T-001", passed=False)
        err = GateViolationError(r)
        assert err.result is r

    def test_message_is_summary(self):
        v = GateViolation(check_id="C1", check_name="x", severity=Priority.P0.value, message="fail")
        r = GateResult(gate_id="G2", task_id="T-002", passed=False, violations=[v])
        err = GateViolationError(r)
        assert str(err) == r.summary()

    def test_passed_result_still_stored(self):
        r = GateResult(gate_id="G3", task_id="T-003", passed=True)
        err = GateViolationError(r)
        assert err.result.passed is True
        assert "[PASS]" in str(err)

    def test_catch_as_gate_engine_error(self):
        r = GateResult(gate_id="G4", task_id="T-004", passed=False)
        with pytest.raises(GateEngineError):
            raise GateViolationError(r)

    def test_catch_as_runtime_error(self):
        r = GateResult(gate_id="G5", task_id="T-005", passed=False)
        with pytest.raises(RuntimeError):
            raise GateViolationError(r)
