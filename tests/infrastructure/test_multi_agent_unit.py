# [A_test] module_id: SRC-TST-2047 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-664 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_multi_agent
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Unit tests for multi_agent.py
"""

from zephyr.infrastructure.a2a_protocol.multi_agent import (
    AgentCard,
    AgentRole,
    DispatchedTask,
    MergeStrategy,
    ResultMerge,
    TaskDispatch,
    TaskStatus,
)


class TestAgentCard:
    def test_create(self):
        card = AgentCard(agent_id="a1", role=AgentRole.BUILDER, capabilities=["python", "yaml"])
        assert card.agent_id == "a1"
        assert card.role == AgentRole.BUILDER
        assert "python" in card.capabilities

    def test_to_dict(self):
        card = AgentCard(agent_id="a2", role=AgentRole.REVIEWER, capabilities=["review"])
        d = card.to_dict()
        assert d["agent_id"] == "a2"
        assert d["role"] == "reviewer"

    def test_from_dict(self):
        data = {
            "agent_id": "a3",
            "role": "tester",
            "capabilities": ["pytest"],
            "description": "test agent",
        }
        card = AgentCard.from_dict(data)
        assert card.agent_id == "a3"
        assert card.role == AgentRole.TESTER
        assert card.description == "test agent"


class TestDispatchedTask:
    def test_lifecycle(self):
        task = DispatchedTask(task_id="t1", agent_id="a1", description="test")
        assert task.status == TaskStatus.PENDING

        task.assign()
        assert task.status == TaskStatus.ASSIGNED

        task.complete({"ok": True})
        assert task.status == TaskStatus.COMPLETED
        assert task.result == {"ok": True}

    def test_fail(self):
        task = DispatchedTask(task_id="t2", agent_id="a1", description="fail test")
        task.fail("error msg")
        assert task.status == TaskStatus.FAILED
        assert task.error == "error msg"


class TestTaskDispatch:
    def test_register_and_assign(self):
        dispatch = TaskDispatch()
        card = AgentCard(agent_id="a1", role=AgentRole.BUILDER, capabilities=["python"])
        dispatch.register_agent(card)

        task = dispatch.assign("t1", "build module")
        assert task is not None
        assert task.agent_id == "a1"
        assert task.status == TaskStatus.ASSIGNED

    def test_assign_no_agents(self):
        dispatch = TaskDispatch()
        task = dispatch.assign("t1", "nobody here")
        assert task is None

    def test_assign_with_role_filter(self):
        dispatch = TaskDispatch()
        dispatch.register_agent(AgentCard("b1", AgentRole.BUILDER))
        dispatch.register_agent(AgentCard("r1", AgentRole.REVIEWER))

        task = dispatch.assign("t1", "review code", required_role=AgentRole.REVIEWER)
        assert task is not None
        assert task.agent_id == "r1"

    def test_assign_to_capable(self):
        dispatch = TaskDispatch()
        dispatch.register_agent(AgentCard("a1", AgentRole.BUILDER, capabilities=["python"]))
        dispatch.register_agent(AgentCard("a2", AgentRole.BUILDER, capabilities=["go"]))

        task = dispatch.assign_to_capable("t1", "go task", "go")
        assert task is not None
        assert task.agent_id == "a2"

    def test_assign_to_capable_no_match(self):
        dispatch = TaskDispatch()
        dispatch.register_agent(AgentCard("a1", AgentRole.BUILDER, capabilities=["python"]))

        task = dispatch.assign_to_capable("t1", "rust task", "rust")
        assert task is None

    def test_unregister_agent(self):
        dispatch = TaskDispatch()
        card = AgentCard("a1", AgentRole.BUILDER)
        dispatch.register_agent(card)
        removed = dispatch.unregister_agent("a1")
        assert removed is not None
        assert dispatch.get_agent("a1") is None

    def test_list_by_role(self):
        dispatch = TaskDispatch()
        dispatch.register_agent(AgentCard("b1", AgentRole.BUILDER))
        dispatch.register_agent(AgentCard("b2", AgentRole.BUILDER))
        dispatch.register_agent(AgentCard("r1", AgentRole.REVIEWER))

        builders = dispatch.list_by_role(AgentRole.BUILDER)
        assert len(builders) == 2


class TestResultMerge:
    def test_vote_strategy(self):
        merge = ResultMerge(strategy=MergeStrategy.VOTE)
        results = [
            {"answer": "A"},
            {"answer": "A"},
            {"answer": "B"},
        ]
        merged = merge.merge(results)
        assert merged["strategy"] == "vote"
        assert merged["winner"] == "A"
        assert merged["vote_count"] == 2

    def test_chain_strategy(self):
        merge = ResultMerge(strategy=MergeStrategy.CHAIN)
        results = [
            {"result": "step1"},
            {"result": "step2", "context": {"k": "v"}},
        ]
        merged = merge.merge(results)
        assert merged["strategy"] == "chain"
        assert len(merged["outputs"]) == 2
        assert merged["context"] == {"k": "v"}

    def test_consensus_reached(self):
        merge = ResultMerge(strategy=MergeStrategy.CONSENSUS)
        results = [
            {"result": "yes"},
            {"result": "yes"},
            {"result": "yes"},
        ]
        merged = merge.merge(results)
        assert merged["consensus_reached"] is True
        assert merged["result"] == "yes"

    def test_consensus_not_reached(self):
        merge = ResultMerge(strategy=MergeStrategy.CONSENSUS)
        results = [
            {"result": "yes"},
            {"result": "no"},
        ]
        merged = merge.merge(results)
        assert merged["consensus_reached"] is False
        assert merged["disagreements"] == 1

    def test_merge_empty(self):
        merge = ResultMerge()
        merged = merge.merge([])
        assert merged["merged"] is True
        assert len(merged["results"]) == 0
