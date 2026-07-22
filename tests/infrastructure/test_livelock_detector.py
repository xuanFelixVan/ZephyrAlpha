# [A_test] module_id: MOD-GOV_livelock_detector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §
# [MODULE] tests.test_livelock_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_livelock_detector.py
# [TTL] task_bound

from zephyr.infrastructure.a2a_protocol.layer3_coordination.livelock_detector import LivelockDetector


class TestLivelockDetector:
    def test_create_default(self):
        ld = LivelockDetector()
        assert ld.cycle_limit == 10

    def test_create_custom_limit(self):
        ld = LivelockDetector(cycle_limit=3)
        assert ld.cycle_limit == 3

    def test_no_cycle_below_limit(self):
        ld = LivelockDetector(cycle_limit=3)
        ld.record_state("agent-a", "state-1")
        ld.record_state("agent-a", "state-1")
        assert ld.check_cycle("agent-a", "state-1") is False

    def test_cycle_detected_at_limit(self):
        ld = LivelockDetector(cycle_limit=3)
        ld.record_state("agent-a", "s1")
        ld.record_state("agent-a", "s1")
        ld.record_state("agent-a", "s1")
        assert ld.check_cycle("agent-a", "s1") is True

    def test_check_cycle_unknown_agent(self):
        ld = LivelockDetector(cycle_limit=3)
        assert ld.check_cycle("agent-x", "s1") is False

    def test_different_states_no_cycle(self):
        ld = LivelockDetector(cycle_limit=3)
        ld.record_state("agent-a", "s1")
        ld.record_state("agent-a", "s2")
        ld.record_state("agent-a", "s3")
        assert ld.check_cycle("agent-a", "s1") is False

    def test_independent_agents(self):
        ld = LivelockDetector(cycle_limit=2)
        ld.record_state("agent-a", "s1")
        ld.record_state("agent-a", "s1")
        assert ld.check_cycle("agent-a", "s1") is True
        assert ld.check_cycle("agent-b", "s1") is False
