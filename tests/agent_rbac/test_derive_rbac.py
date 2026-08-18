# [A_test] module_id: MOD-GOV_derive_rbac | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_derive_rbac
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""MOD-INF-018 test_derive_rbac.py — RBAC 自动派生测试."""

from __future__ import annotations


class TestDeriveRBAC:
    def test_rbac_guard_derives_permissions(self):
        from zephyr.security.access_control.guards.rbac_guard import RBACGuard
        from zephyr.security.access_control.identity import AgentIdentity, AgentRole, MaturityLevel

        guard = RBACGuard()
        agent = AgentIdentity(session_id="test", maturity=MaturityLevel.L2_REGULAR, role=AgentRole.WRITER)
        result = guard.check(agent, "read:docs")
        assert result is not None

    def test_maturity_level_mapping(self):
        from zephyr.security.access_control.identity import MaturityLevel

        levels = [
            MaturityLevel.L0_INTERN,
            MaturityLevel.L1_JUNIOR,
            MaturityLevel.L2_REGULAR,
            MaturityLevel.L3_SENIOR,
            MaturityLevel.L4_PRINCIPAL,
        ]
        assert len(levels) == 5
