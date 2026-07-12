# [A_test] module_id: SRC-TST-0287 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_agent_lifecycle
# [INVARIANTS] retire sets agent status to RETIRED
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.actors.agent_lifecycle import AgentLifecycle


class TestAgentLifecycleInstantiation:
    def test_default_construction(self):
        al = AgentLifecycle()
        assert al.agents == {}

    def test_custom_agents(self):
        agents = {"agent-1": "ACTIVE", "agent-2": "ACTIVE"}
        al = AgentLifecycle(agents=agents)
        assert al.agents == agents


class TestRetire:
    def test_retire_sets_retired(self):
        al = AgentLifecycle(agents={"agent-1": "ACTIVE"})
        al.retire("agent-1")
        assert al.agents["agent-1"] == "RETIRED"

    def test_retire_new_agent(self):
        al = AgentLifecycle()
        al.retire("agent-new")
        assert al.agents["agent-new"] == "RETIRED"

    def test_retire_already_retired(self):
        al = AgentLifecycle(agents={"agent-1": "RETIRED"})
        al.retire("agent-1")
        assert al.agents["agent-1"] == "RETIRED"

    def test_retire_preserves_other_agents(self):
        al = AgentLifecycle(agents={"agent-1": "ACTIVE", "agent-2": "ACTIVE"})
        al.retire("agent-1")
        assert al.agents["agent-1"] == "RETIRED"
        assert al.agents["agent-2"] == "ACTIVE"

    def test_retire_empty_id(self):
        al = AgentLifecycle()
        al.retire("")
        assert al.agents[""] == "RETIRED"
