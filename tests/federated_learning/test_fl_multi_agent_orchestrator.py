# [A_test] module_id: SRC-TST-0974 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_multi_agent_orchestrator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.actors.multi_agent_orchestrator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_multi_agent_orchestrator.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.actors.multi_agent_orchestrator import MultiAgentOrchestrator


class TestMultiAgentOrchestratorInstantiation:
    def test_creates_with_defaults(self):
        orc = MultiAgentOrchestrator()
        assert orc.agents == {}

    def test_creates_with_agents(self):
        orc = MultiAgentOrchestrator(agents={"a1": "diagnosis", "a2": "repair"})
        assert len(orc.agents) == 2


class TestDelegate:
    def test_delegate_to_known_agent(self):
        orc = MultiAgentOrchestrator(agents={"a1": "diagnosis"})
        assert orc.delegate("task1", "a1") is True

    def test_delegate_to_unknown_agent(self):
        orc = MultiAgentOrchestrator(agents={"a1": "diagnosis"})
        assert orc.delegate("task1", "unknown") is False

    def test_delegate_boundary_empty_agents(self):
        orc = MultiAgentOrchestrator()
        assert orc.delegate("task1", "a1") is False

    def test_delegate_boundary_empty_task(self):
        orc = MultiAgentOrchestrator(agents={"a1": "diagnosis"})
        assert orc.delegate("", "a1") is True
