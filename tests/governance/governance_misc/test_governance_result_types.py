# [A_test] module_id: MOD-GOV_governance_result_types | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_governance_result_types
# [DOMAIN] D_GOV_CODE_QUALITY
# [INVARIANTS] Re-exports must match canonical source; RollbackStatus/ValidationResult enums must be complete
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if canonical source missing; ValueError on invalid enum
# [TESTS] tests/test_governance_result_types.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.governance.escalation.result_types import RollbackResult, RollbackStatus, ValidationResult


class TestReExports:
    def test_rollback_status_is_enum(self):
        assert issubclass(RollbackStatus, str)

    def test_validation_result_is_enum(self):
        assert issubclass(ValidationResult, str)

    def test_rollback_result_is_base_model(self):
        from pydantic import BaseModel

        assert issubclass(RollbackResult, BaseModel)

    def test_all_exported_names_in___all__(self):
        from zephyr.governance import result_types as rt

        assert "RollbackResult" in rt.__all__
        assert "RollbackStatus" in rt.__all__
        assert "ValidationResult" in rt.__all__


class TestRollbackStatusEnum:
    def test_has_success(self):
        assert RollbackStatus.SUCCESS == "SUCCESS"

    def test_has_failed(self):
        assert RollbackStatus.FAILED == "FAILED"

    def test_has_partial(self):
        assert RollbackStatus.PARTIAL == "PARTIAL"

    def test_all_members_count(self):
        assert len(RollbackStatus) == 3


class TestValidationResultEnum:
    def test_has_pass(self):
        assert ValidationResult.PASS == "PASS"

    def test_has_fail(self):
        assert ValidationResult.FAIL == "FAIL"

    def test_has_pending(self):
        assert ValidationResult.PENDING == "PENDING"

    def test_all_members_count(self):
        assert len(ValidationResult) == 3


class TestRollbackResultModel:
    def test_create_with_required_fields(self):
        result = RollbackResult(rollback_id="rb-001", target="commit_abc")
        assert result.rollback_id == "rb-001"
        assert result.target == "commit_abc"

    def test_default_status_is_success(self):
        result = RollbackResult(rollback_id="rb-002", target="t")
        assert result.status == RollbackStatus.SUCCESS

    def test_default_validation_result_is_pending(self):
        result = RollbackResult(rollback_id="rb-003", target="t")
        assert result.validation_result == ValidationResult.PENDING

    def test_default_error_detail_is_empty(self):
        result = RollbackResult(rollback_id="rb-004", target="t")
        assert result.error_detail == ""

    def test_needs_escalation_when_failed(self):
        result = RollbackResult(
            rollback_id="rb-005",
            target="t",
            status=RollbackStatus.FAILED,
        )
        assert result.needs_escalation is True

    def test_needs_escalation_when_validation_fail(self):
        result = RollbackResult(
            rollback_id="rb-006",
            target="t",
            validation_result=ValidationResult.FAIL,
        )
        assert result.needs_escalation is True

    def test_needs_no_escalation_when_success_and_pass(self):
        result = RollbackResult(
            rollback_id="rb-007",
            target="t",
            status=RollbackStatus.SUCCESS,
            validation_result=ValidationResult.PASS,
        )
        assert result.needs_escalation is False

    def test_needs_escalation_when_partial_and_fail(self):
        result = RollbackResult(
            rollback_id="rb-008",
            target="t",
            status=RollbackStatus.PARTIAL,
            validation_result=ValidationResult.FAIL,
        )
        assert result.needs_escalation is True


class TestRollbackResultBoundaryCases:
    def test_create_with_all_fields(self):
        result = RollbackResult(
            rollback_id="rb-009",
            target="commit_xyz",
            status=RollbackStatus.FAILED,
            validation_result=ValidationResult.FAIL,
            error_detail="Connection timeout",
            agent_id="agent-1",
            resource_path="src/main.py",
        )
        assert result.rollback_id == "rb-009"
        assert result.status == RollbackStatus.FAILED
        assert result.error_detail == "Connection timeout"
        assert result.agent_id == "agent-1"
        assert result.resource_path == "src/main.py"

    def test_empty_string_fields(self):
        result = RollbackResult(rollback_id="", target="")
        assert result.rollback_id == ""
        assert result.target == ""

    def test_detected_at_auto_generated(self):
        result = RollbackResult(rollback_id="rb-010", target="t")
        assert len(result.detected_at) > 0

    def test_missing_required_field_raises_error(self):
        with pytest.raises(Exception):
            RollbackResult(rollback_id="rb-011")
