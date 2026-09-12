# [A_test] module_id: MOD-GOV_cascade_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §
# [MODULE] tests.test_cascade_guard
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_cascade_guard.py
# [TTL] task_bound

from zephyr.infrastructure.a2a_protocol.layer3_coordination.cascade_guard import CascadeGuard


class TestCascadeGuard:
    def test_create_default_threshold(self):
        cg = CascadeGuard()
        assert cg.threshold == 5

    def test_create_custom_threshold(self):
        cg = CascadeGuard(threshold=3)
        assert cg.threshold == 3

    def test_check_below_threshold(self):
        cg = CascadeGuard(threshold=3)
        cg.record_failure("agent-a")
        cg.record_failure("agent-a")
        assert cg.check("agent-a") is True

    def test_check_at_threshold(self):
        cg = CascadeGuard(threshold=3)
        for _ in range(3):
            cg.record_failure("agent-a")
        assert cg.check("agent-a") is False

    def test_check_above_threshold(self):
        cg = CascadeGuard(threshold=2)
        cg.record_failure("agent-a")
        cg.record_failure("agent-a")
        cg.record_failure("agent-a")
        assert cg.check("agent-a") is False

    def test_check_unknown_agent(self):
        cg = CascadeGuard()
        assert cg.check("unknown-agent") is True

    def test_record_failure_returns_count(self):
        cg = CascadeGuard()
        assert cg.record_failure("agent-a") == 1
        assert cg.record_failure("agent-a") == 2

    def test_independent_agents(self):
        cg = CascadeGuard(threshold=2)
        cg.record_failure("agent-a")
        cg.record_failure("agent-a")
        assert cg.check("agent-a") is False
        assert cg.check("agent-b") is True
