# [A_test] module_id: SRC-TST-0929 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_agent_lifecycle
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.actors.agent_lifecycle
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_agent_lifecycle.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.actors.agent_lifecycle import AgentLifecycle


class TestAgentLifecycleInstantiation:
    def test_creates_with_defaults(self):
        lifecycle = AgentLifecycle()
        assert lifecycle.agents == {}

    def test_creates_with_existing_agents(self):
        lifecycle = AgentLifecycle(agents={"a1": "ACTIVE", "a2": "IDLE"})
        assert len(lifecycle.agents) == 2


class TestRetire:
    def test_retire_marks_agent_retired(self):
        lifecycle = AgentLifecycle(agents={"a1": "ACTIVE"})
        lifecycle.retire("a1")
        assert lifecycle.agents["a1"] == "RETIRED"

    def test_retire_new_agent_id(self):
        lifecycle = AgentLifecycle()
        lifecycle.retire("unknown_agent")
        assert lifecycle.agents["unknown_agent"] == "RETIRED"

    def test_retire_boundary_empty_id(self):
        lifecycle = AgentLifecycle()
        lifecycle.retire("")
        assert lifecycle.agents[""] == "RETIRED"
