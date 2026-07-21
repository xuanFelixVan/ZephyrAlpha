# [A_test] module_id: MOD-GOV_guard_layers_agent_rbac | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_guard_layers
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""测试防护层模块 — ColdStartLock, AutoGuard, EscalationHandler"""

from zephyr.security.access_control.guard_layers import AutoGuard, ColdStartLock, EscalationHandler
from zephyr.security.access_control.identity import AgentIdentity, MaturityLevel


class TestColdStartLock:
    def test_initial_locked(self):
        lock = ColdStartLock()
        assert lock.is_locked

    def test_owner_bypass_unlocks(self):
        lock = ColdStartLock()
        lock.owner_bypass()
        assert not lock.is_locked


class TestAutoGuard:
    def test_allow_with_guard(self):
        guard = AutoGuard()
        agent = AgentIdentity(session_id="ag-test", maturity=MaturityLevel.L2_REGULAR)
        result = guard.allow_with_guard(agent, "write:src")
        assert result.decision == "AUTO_GUARD"
        assert result.timeout == 600

    def test_get_active_guards(self):
        guard = AutoGuard()
        agent = AgentIdentity(session_id="ag-test-2")
        guard.allow_with_guard(agent, "write:src")
        active = guard.get_active_guards("ag-test-2")
        assert len(active) == 1


class TestEscalationHandler:
    def test_p0_triggers_notify(self):
        handler = EscalationHandler()
        result = handler.escalate("agent-e", "P0_OWNER", "Critical breach")
        assert "NOTIFY_OWNER" in result

    def test_should_throttle_under_limit(self):
        handler = EscalationHandler()
        for _ in range(3):
            handler.escalate("agent-e2", "P4_LOW", "test")
        assert not handler.should_throttle("agent-e2", max_count=5)

    def test_reset_agent(self):
        handler = EscalationHandler()
        handler.escalate("agent-e3", "P0_OWNER", "critical")
        handler.reset_agent("agent-e3")
        assert not handler.should_throttle("agent-e3")
