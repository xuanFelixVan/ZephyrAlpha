# [A_test] module_id: MOD-GOV_escalation_adapter | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_escalation_adapter
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_escalation_adapter.py -q
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import patch

from zephyr.governance.services.adapter import (
    EscalationDecision,
    OperationType,
    check_operation,
    escalate_if_needed,
)


class TestOperationType:
    def test_all_operation_types_are_strings(self):
        for ot in OperationType:
            assert isinstance(ot.value, str)

    def test_security_violation_value(self):
        assert OperationType.SECURITY_VIOLATION.value == "security_violation"

    def test_custom_value(self):
        assert OperationType.CUSTOM.value == "custom"

    def test_operation_type_from_string(self):
        assert OperationType("deadlock") == OperationType.DEADLOCK

    def test_invalid_operation_type_raises(self):
        try:
            OperationType("nonexistent_type")
            assert False, "Expected ValueError"
        except ValueError:
            assert True


class TestEscalationDecision:
    def test_default_values(self):
        d = EscalationDecision(operation="test")
        assert d.operation == "test"
        assert d.should_block is False
        assert d.should_escalate is False
        assert d.should_delegate is False
        assert d.escalation_level == "L0_SELF_HEAL"
        assert d.reason == ""
        assert d.suggested_delegate == ""
        assert d.circuit_state == "CLOSED"

    def test_custom_values(self):
        d = EscalationDecision(
            operation="op",
            should_block=True,
            should_escalate=True,
            escalation_level="L4_EMERGENCY",
            reason="critical",
        )
        assert d.should_block is True
        assert d.escalation_level == "L4_EMERGENCY"


class TestEscalateIfNeeded:
    def test_returns_pass_through_when_engine_unavailable(self):
        with patch("zephyr.governance.services.adapter._get_engine", return_value=None):
            result = escalate_if_needed("security_violation", "test desc")
            assert result.should_block is False
            assert "pass-through" in result.reason

    def test_returns_decision_with_operation_type(self):
        with patch("zephyr.governance.services.adapter._get_engine", return_value=None):
            result = escalate_if_needed("timeout", "timeout desc")
            assert result.operation == "timeout"

    def test_returns_decision_with_owner_id(self):
        with patch("zephyr.governance.services.adapter._get_engine", return_value=None):
            result = escalate_if_needed("custom", "desc", owner_id="sess-1")
            assert result.operation == "custom"


class TestCheckOperation:
    def test_detects_rm_rf_as_security_violation(self):
        with patch("zephyr.governance.services.adapter._get_engine", return_value=None):
            result = check_operation("rm -rf /tmp/junk")
            assert result.operation == "security_violation"

    def test_detects_drop_as_security_violation(self):
        with patch("zephyr.governance.services.adapter._get_engine", return_value=None):
            result = check_operation("DROP TABLE users")
            assert result.operation == "security_violation"

    def test_detects_deadlock(self):
        with patch("zephyr.governance.services.adapter._get_engine", return_value=None):
            result = check_operation("deadlock detected in pipeline")
            assert result.operation == "deadlock"

    def test_detects_budget_exceeded(self):
        with patch("zephyr.governance.services.adapter._get_engine", return_value=None):
            result = check_operation("budget: exceeded limit")
            assert result.operation == "budget_exceeded"

    def test_detects_timeout(self):
        with patch("zephyr.governance.services.adapter._get_engine", return_value=None):
            result = check_operation("timeout waiting for response")
            assert result.operation == "timeout"

    def test_detects_cascade_failure(self):
        with patch("zephyr.governance.services.adapter._get_engine", return_value=None):
            result = check_operation("cascade failure in module")
            assert result.operation == "cascade_failure"

    def test_detects_owner_absent(self):
        with patch("zephyr.governance.services.adapter._get_engine", return_value=None):
            result = check_operation("owner absent for review")
            assert result.operation == "owner_absent"

    def test_defaults_to_custom_for_unknown(self):
        with patch("zephyr.governance.services.adapter._get_engine", return_value=None):
            result = check_operation("normal operation")
            assert result.operation == "custom"

    def test_case_insensitive_detection(self):
        with patch("zephyr.governance.services.adapter._get_engine", return_value=None):
            result = check_operation("RM -RF /everything")
            assert result.operation == "security_violation"


class TestCheckOperationBoundary:
    def test_empty_operation_string(self):
        with patch("zephyr.governance.services.adapter._get_engine", return_value=None):
            result = check_operation("")
            assert result.operation == "custom"

    def test_operation_with_target_path(self):
        with patch("zephyr.governance.services.adapter._get_engine", return_value=None):
            result = check_operation("rm -rf /data", target_path="/data/important")
            assert "path=/data/important" in result.reason or result.operation == "security_violation"

    def test_operation_with_session_id(self):
        with patch("zephyr.governance.services.adapter._get_engine", return_value=None):
            result = check_operation("deadlock", session_id="sess-123")
            assert result.operation == "deadlock"
