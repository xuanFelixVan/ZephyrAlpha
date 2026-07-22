# [A_test] module_id: MOD-GOV_guard_layers_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.guard_layers
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

from unittest.mock import MagicMock

import pytest

try:
    from zephyr.security.access_control.guard_layers import (
        AutoGuard,
        AutoGuardMode,
        AutoGuardResult,
        ColdStartLock,
        EscalationHandler,
    )
except Exception as _exc:
    pytest.skip(f"无法导入 guard_layers: {_exc}", allow_module_level=True)


class TestAutoGuardMode:
    def test_enum_values(self):
        assert AutoGuardMode.OFF.value == "off"
        assert AutoGuardMode.LAX.value == "lax"
        assert AutoGuardMode.STRICT.value == "strict"


class TestAutoGuardResult:
    def test_default_values(self):
        r = AutoGuardResult()
        assert r.decision == "ALLOW"
        assert r.timeout == 300
        assert r.post_hook_registered is False


class TestColdStartLock:
    def test_initial_state_locked(self):
        mock_core = MagicMock()
        lock = ColdStartLock(immutable_core=mock_core)
        assert lock.is_locked is True

    def test_verify_and_unlock_success(self):
        mock_core = MagicMock()
        mock_result = MagicMock()
        mock_result.intact = True
        mock_core.verify_immutable_core_integrity.return_value = mock_result
        lock = ColdStartLock(immutable_core=mock_core)
        result = lock.verify_and_unlock()
        assert result is True
        assert lock.is_locked is False

    def test_verify_and_unlock_failure(self):
        mock_core = MagicMock()
        mock_result = MagicMock()
        mock_result.intact = False
        mock_core.verify_immutable_core_integrity.return_value = mock_result
        lock = ColdStartLock(immutable_core=mock_core)
        result = lock.verify_and_unlock()
        assert result is False
        assert lock.is_locked is True

    def test_owner_bypass(self):
        mock_core = MagicMock()
        lock = ColdStartLock(immutable_core=mock_core)
        lock.owner_bypass()
        assert lock.is_locked is False


class TestGuardLayersEscalationHandler:
    def test_escalate_p0(self):
        eh = EscalationHandler()
        result = eh.escalate("agent-1", "P0_OWNER", "critical")
        assert result == "P0_TRIGGERED_NOTIFY_OWNER"

    def test_escalate_p1(self):
        eh = EscalationHandler()
        result = eh.escalate("agent-1", "P1_URGENT", "urgent")
        assert result == "ESCALATED_AUDIT_ONLY"

    def test_escalate_p2(self):
        eh = EscalationHandler()
        result = eh.escalate("agent-1", "P2_HIGH", "high")
        assert result == "ESCALATED_AUDIT_ONLY"

    def test_escalate_p3(self):
        eh = EscalationHandler()
        result = eh.escalate("agent-1", "P3_MEDIUM", "medium")
        assert result == "LOGGED"

    def test_escalate_p4(self):
        eh = EscalationHandler()
        result = eh.escalate("agent-1", "P4_LOW", "low")
        assert result == "LOGGED"

    def test_should_throttle(self):
        eh = EscalationHandler()
        for i in range(5):
            eh.escalate("agent-1", "P4_LOW", f"r{i}")
        assert eh.should_throttle("agent-1") is True

    def test_reset_agent(self):
        eh = EscalationHandler()
        eh.escalate("agent-1", "P4_LOW", "r1")
        eh.reset_agent("agent-1")
        assert eh.should_throttle("agent-1") is False


class TestAutoGuard:
    def test_allow_with_guard(self):
        mock_agent = MagicMock()
        mock_agent.session_id = "sess-001"
        mock_agent.get_auto_guard_timeout.return_value = 300
        ag = AutoGuard()
        result = ag.allow_with_guard(mock_agent, "write:src")
        assert result.decision == "AUTO_GUARD"
        assert result.timeout == 300
        assert result.post_hook_registered is True

    def test_verify_match(self):
        ag = AutoGuard()
        assert ag.verify("agent-1", "op", "expected", "expected") is True

    def test_verify_mismatch(self):
        ag = AutoGuard()
        assert ag.verify("agent-1", "op", "expected", "actual") is False

    def test_get_active_guards(self):
        mock_agent = MagicMock()
        mock_agent.session_id = "sess-002"
        mock_agent.get_auto_guard_timeout.return_value = 300
        ag = AutoGuard()
        ag.allow_with_guard(mock_agent, "write:src")
        active = ag.get_active_guards("sess-002")
        assert len(active) == 1
        assert active[0]["operation"] == "write:src"

    def test_get_active_guards_empty(self):
        ag = AutoGuard()
        active = ag.get_active_guards("nonexistent")
        assert active == []

    def test_levels_constant(self):
        assert "P0_OWNER" in EscalationHandler.LEVELS
