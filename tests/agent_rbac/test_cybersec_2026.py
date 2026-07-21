# [A_test] module_id: MOD-GOV_cybersec | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_cybersec_2026
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""cybersec 2026 独立测试."""

from __future__ import annotations

from zephyr.security.access_control.guards.cybersec_2026_guard import Cybersec2026Guard


class TestCybersec2026:
    def test_no_threat(self):
        guard = Cybersec2026Guard()
        result = guard.scan({"safe": True})
        assert result.detected is False

    def test_agent_supply_chain(self):
        guard = Cybersec2026Guard()
        result = guard.scan({"unsigned_agent_package": True})
        assert result.detected is True

    def test_multi_threat_high_severity(self):
        guard = Cybersec2026Guard()
        result = guard.scan({"untrusted_hub": True, "hidden_training_trigger": True})
        assert result.severity == "HIGH"
