# [A_test] module_id: MOD-GOV_integrity_agent_rbac | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_integrity
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""完整性自检测试."""

from __future__ import annotations

from zephyr.security.access_control.integrity_self_check import IntegritySelfCheck


class TestIntegrity:
    def test_check_all_modules(self):
        checker = IntegritySelfCheck()
        results = checker.check_all()
        assert len(results) >= 55
        assert all(r.passed for r in results)

    def test_summary(self):
        checker = IntegritySelfCheck()
        results = checker.check_all()
        summary = checker.summary()
        assert summary["total_modules"] >= 55
        assert summary["passed"] >= 55
        assert summary["all_ok"] is True
