# [A_test] module_id: MOD-GOV_result_types | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_result_types
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] RollbackResult字段不可删;status/validation_result枚举不可改值
# [MODIFY-GUARD] contracts_blueprint.md §4;src/zephyr/rollback/__init__.py
# [CONSUMERS] CI;pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValidationError;ValueError
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.governance.escalation.result_types import RollbackResult, RollbackStatus, ValidationResult


class TestRollbackStatus:
    def test_enum_values(self):
        assert RollbackStatus.SUCCESS.value == "SUCCESS"
        assert RollbackStatus.FAILED.value == "FAILED"
        assert RollbackStatus.PARTIAL.value == "PARTIAL"

    def test_member_count(self):
        assert len(RollbackStatus) == 3

    def test_enum_is_str(self):
        for member in RollbackStatus:
            assert isinstance(member, str)

    def test_from_value(self):
        assert RollbackStatus("FAILED") is RollbackStatus.FAILED

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            RollbackStatus("UNKNOWN")


class TestValidationResult:
    def test_enum_values(self):
        assert ValidationResult.PASS.value == "PASS"
        assert ValidationResult.FAIL.value == "FAIL"
        assert ValidationResult.PENDING.value == "PENDING"

    def test_member_count(self):
        assert len(ValidationResult) == 3

    def test_from_value(self):
        assert ValidationResult("PASS") is ValidationResult.PASS

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            ValidationResult("INVALID")


class TestRollbackResult:
    def test_instantiation_defaults(self):
        r = RollbackResult(rollback_id="rb-001", target="file.py")
        assert r.rollback_id == "rb-001"
        assert r.target == "file.py"
        assert r.status is RollbackStatus.SUCCESS
        assert r.validation_result is ValidationResult.PENDING
        assert r.error_detail == ""
        assert r.agent_id == ""
        assert r.resource_path == ""

    def test_instantiation_all_fields(self):
        r = RollbackResult(
            rollback_id="rb-002",
            target="module.py",
            status=RollbackStatus.FAILED,
            validation_result=ValidationResult.FAIL,
            error_detail="timeout",
            detected_at="2026-01-01T00:00:00",
            agent_id="agent-1",
            resource_path="/src/module.py",
        )
        assert r.status is RollbackStatus.FAILED
        assert r.validation_result is ValidationResult.FAIL
        assert r.error_detail == "timeout"
        assert r.agent_id == "agent-1"
        assert r.resource_path == "/src/module.py"

    def test_needs_escalation_on_failed_status(self):
        r = RollbackResult(rollback_id="rb-003", target="f.py", status=RollbackStatus.FAILED)
        assert r.needs_escalation is True

    def test_needs_escalation_on_fail_validation(self):
        r = RollbackResult(
            rollback_id="rb-004",
            target="f.py",
            validation_result=ValidationResult.FAIL,
        )
        assert r.needs_escalation is True

    def test_needs_escalation_false_on_success(self):
        r = RollbackResult(
            rollback_id="rb-005",
            target="f.py",
            status=RollbackStatus.SUCCESS,
            validation_result=ValidationResult.PASS,
        )
        assert r.needs_escalation is False

    def test_needs_escalation_partial_no_fail(self):
        r = RollbackResult(
            rollback_id="rb-006",
            target="f.py",
            status=RollbackStatus.PARTIAL,
            validation_result=ValidationResult.PENDING,
        )
        assert r.needs_escalation is False

    def test_missing_required_field_raises(self):
        with pytest.raises(Exception):
            RollbackResult()

    def test_empty_string_fields(self):
        r = RollbackResult(rollback_id="", target="")
        assert r.rollback_id == ""
        assert r.target == ""
