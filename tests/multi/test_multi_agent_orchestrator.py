# [A_test] module_id: SRC-TST-1298 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_multi_agent_orchestrator
# [INVARIANTS] delegate returns True iff agent_id in agents
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.actors.multi_agent_orchestrator import MultiAgentOrchestrator


class TestMultiAgentOrchestratorInstantiation:
    def test_default_construction(self):
        mao = MultiAgentOrchestrator()
        assert mao.agents == {}

    def test_custom_agents(self):
        agents = {"agent-1": "repair", "agent-2": "monitor"}
        mao = MultiAgentOrchestrator(agents=agents)
        assert mao.agents == agents
        assert len(mao.agents) == 2


class TestDelegate:
    def test_delegate_to_existing_agent(self):
        mao = MultiAgentOrchestrator(agents={"agent-1": "repair"})
        assert mao.delegate(task="fix_disk", agent_id="agent-1") is True

    def test_delegate_to_nonexistent_agent(self):
        mao = MultiAgentOrchestrator(agents={"agent-1": "repair"})
        assert mao.delegate(task="fix_disk", agent_id="agent-99") is False

    def test_delegate_empty_agents(self):
        mao = MultiAgentOrchestrator()
        assert mao.delegate(task="any", agent_id="agent-1") is False

    def test_delegate_multiple_agents(self):
        mao = MultiAgentOrchestrator(agents={"a1": "repair", "a2": "monitor", "a3": "deploy"})
        assert mao.delegate(task="t1", agent_id="a2") is True
        assert mao.delegate(task="t2", agent_id="a4") is False
