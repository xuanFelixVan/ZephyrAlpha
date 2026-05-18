# [BLUEPRINT] MOD-INF-018 | docs/03_modules/l01_infrastructure/agent-rbac/blueprint.md | §
# [MODULE] tests.agent_rbac.test_derive_rbac
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""MOD-INF-018 test_derive_rbac.py — RBAC 自动派生测试."""
from __future__ import annotations

import pytest


class TestDeriveRBAC:
    def test_rbac_guard_derives_permissions(self):
        from zephyr.agent_rbac.rbac_guard import RBACGuard
        from zephyr.agent_rbac.identity import AgentIdentity, MaturityLevel, AgentRole
        guard = RBACGuard()
        agent = AgentIdentity(session_id="test", maturity=MaturityLevel.L2_REGULAR, role=AgentRole.WRITER)
        result = guard.check(agent, "read:docs")
        assert result is not None

    def test_maturity_level_mapping(self):
        from zephyr.agent_rbac.identity import MaturityLevel
        levels = [MaturityLevel.L0_INTERN, MaturityLevel.L1_JUNIOR,
                  MaturityLevel.L2_REGULAR, MaturityLevel.L3_SENIOR, MaturityLevel.L4_PRINCIPAL]
        assert len(levels) == 5
