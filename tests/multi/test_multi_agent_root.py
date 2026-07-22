# [A_test] module_id: MOD-GOV_multi_agent_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §
# [MODULE] tests.test_multi_agent
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_multi_agent_root.py
# [TTL] task_bound

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
        card = AgentCard(agent_id="b1", role=AgentRole.BUILDER, capabilities=["python"])
        assert card.agent_id == "b1"
        assert card.role == AgentRole.BUILDER

    def test_to_dict(self):
        card = AgentCard(agent_id="b1", role=AgentRole.BUILDER, capabilities=["python"])
        d = card.to_dict()
        assert d["agent_id"] == "b1"
        assert d["role"] == "builder"

    def test_from_dict(self):
        data = {"agent_id": "r1", "role": "reviewer", "capabilities": ["review"]}
        card = AgentCard.from_dict(data)
        assert card.agent_id == "r1"
        assert card.role == AgentRole.REVIEWER


class TestDispatchedTask:
    def test_create(self):
        task = DispatchedTask(task_id="t1", agent_id="b1", description="build")
        assert task.status == TaskStatus.PENDING

    def test_assign(self):
        task = DispatchedTask(task_id="t1", agent_id="b1", description="build")
        task.assign()
        assert task.status == TaskStatus.ASSIGNED
        assert task.assigned_at is not None

    def test_complete(self):
        task = DispatchedTask(task_id="t1", agent_id="b1", description="build")
        task.assign()
        task.start()
        task.complete(result={"ok": True})
        assert task.status == TaskStatus.COMPLETED
        assert task.result == {"ok": True}

    def test_fail(self):
        task = DispatchedTask(task_id="t1", agent_id="b1", description="build")
        task.fail(error="crash")
        assert task.status == TaskStatus.FAILED
        assert task.error == "crash"


class TestTaskDispatch:
    def test_register_and_assign(self):
        td = TaskDispatch()
        card = AgentCard(agent_id="b1", role=AgentRole.BUILDER)
        td.register_agent(card)
        task = td.assign("t1", "build module")
        assert task is not None
        assert task.agent_id == "b1"

    def test_assign_by_role(self):
        td = TaskDispatch()
        td.register_agent(AgentCard(agent_id="b1", role=AgentRole.BUILDER))
        td.register_agent(AgentCard(agent_id="r1", role=AgentRole.REVIEWER))
        task = td.assign("t1", "review code", required_role=AgentRole.REVIEWER)
        assert task is not None
        assert task.agent_id == "r1"

    def test_assign_no_agents(self):
        td = TaskDispatch()
        task = td.assign("t1", "build")
        assert task is None

    def test_assign_to_capable(self):
        td = TaskDispatch()
        td.register_agent(AgentCard(agent_id="b1", role=AgentRole.BUILDER, capabilities=["python"]))
        task = td.assign_to_capable("t1", "write code", "python")
        assert task is not None

    def test_assign_to_capable_no_match(self):
        td = TaskDispatch()
        td.register_agent(AgentCard(agent_id="b1", role=AgentRole.BUILDER, capabilities=["rust"]))
        task = td.assign_to_capable("t1", "write code", "python")
        assert task is None

    def test_unregister_agent(self):
        td = TaskDispatch()
        td.register_agent(AgentCard(agent_id="b1", role=AgentRole.BUILDER))
        removed = td.unregister_agent("b1")
        assert removed is not None
        assert td.get_agent("b1") is None

    def test_list_by_role(self):
        td = TaskDispatch()
        td.register_agent(AgentCard(agent_id="b1", role=AgentRole.BUILDER))
        td.register_agent(AgentCard(agent_id="b2", role=AgentRole.BUILDER))
        td.register_agent(AgentCard(agent_id="r1", role=AgentRole.REVIEWER))
        builders = td.list_by_role(AgentRole.BUILDER)
        assert len(builders) == 2


class TestResultMerge:
    def test_merge_empty(self):
        rm = ResultMerge()
        result = rm.merge([])
        assert result["merged"] is True

    def test_merge_vote(self):
        rm = ResultMerge(strategy=MergeStrategy.VOTE)
        results = [{"answer": "yes"}, {"answer": "yes"}, {"answer": "no"}]
        result = rm.merge(results)
        assert result["strategy"] == "vote"
        assert result["winner"] == "yes"

    def test_merge_chain(self):
        rm = ResultMerge(strategy=MergeStrategy.CHAIN)
        results = [{"result": "step1", "context": {"k": "v1"}}, {"result": "step2", "context": {"k2": "v2"}}]
        result = rm.merge(results)
        assert result["strategy"] == "chain"
        assert len(result["outputs"]) == 2

    def test_merge_consensus_agreed(self):
        rm = ResultMerge(strategy=MergeStrategy.CONSENSUS)
        results = [{"result": "same"}, {"result": "same"}]
        result = rm.merge(results)
        assert result["consensus_reached"] is True

    def test_merge_consensus_disagreed(self):
        rm = ResultMerge(strategy=MergeStrategy.CONSENSUS)
        results = [{"result": "yes"}, {"result": "no"}]
        result = rm.merge(results)
        assert result["consensus_reached"] is False
