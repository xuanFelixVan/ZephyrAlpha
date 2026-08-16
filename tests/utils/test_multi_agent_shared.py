# [A_test] module_id: MOD-GOV_multi_agent_shared | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-569 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.shared.test_multi_agent
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
单元测试：src/zephyr/shared/multi_agent.py
============================================
覆盖矩阵：
  AgentRole / TaskStatus / MergeStrategy：
    - 枚举值完整性 × 3
  AgentCard：
    - 构造 × 1
    - to_dict / from_dict 环形 × 1
    - 默认值 × 1
  DispatchedTask：
    - 初始化状态 PENDING × 1
    - assign / start / complete / fail 状态转换 × 5
  TaskDispatch：
    - register_agent / unregister_agent × 2
    - assign 按 role 分派 × 3
    - assign_to_capable × 2
    - get_agent / list_by_role × 2
  ResultMerge：
    - VOTE 策略 × 2
    - CHAIN 策略 × 1
    - CONSENSUS 策略 × 3
    - 空结果 × 1

Safety: LOW（编排基座，不直接影响安全）
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


class TestEnums:
    def test_agent_roles(self):
        values = {r.value for r in AgentRole}
        assert "coordinator" in values
        assert "builder" in values
        assert "reviewer" in values
        assert "tester" in values
        assert "auditor" in values
        assert "researcher" in values
        assert len(values) == 6

    def test_task_statuses(self):
        # SSoT: zephyr.gov_enforcement.rule_enforcement.task_types.TaskStatus
        values = {s.value for s in TaskStatus}
        assert values == {
            "PENDING",
            "CREATED",
            "LOCKED",
            "ASSIGNED",
            "READY",
            "IN_PROGRESS",
            "REVIEWING",
            "COMPLETED",
            "VERIFIED",
            "FAILED",
            "BLOCKED",
            "WAITING",
            "RETRY",
            "CANCELLED",
        }

    def test_merge_strategies(self):
        values = {s.value for s in MergeStrategy}
        assert "vote" in values
        assert "chain" in values
        assert "consensus" in values
        assert len(values) == 3


class TestAgentCard:
    def test_construction(self):
        card = AgentCard(
            agent_id="builder-01",
            role=AgentRole.BUILDER,
            capabilities=["python", "pytest"],
            description="Code gen agent",
            endpoint="http://localhost:8001",
            metadata={"version": "1.0"},
        )
        assert card.agent_id == "builder-01"
        assert card.role == AgentRole.BUILDER
        assert "python" in card.capabilities
        assert card.endpoint == "http://localhost:8001"

    def test_to_dict_from_dict_roundtrip(self):
        card = AgentCard(
            agent_id="reviewer-01",
            role=AgentRole.REVIEWER,
            capabilities=["code-review"],
            description="Review agent",
            endpoint="http://localhost:8002",
        )
        d = card.to_dict()
        restored = AgentCard.from_dict(d)
        assert restored.agent_id == card.agent_id
        assert restored.role == card.role
        assert restored.capabilities == card.capabilities

    def test_defaults(self):
        card = AgentCard(agent_id="minimal", role=AgentRole.RESEARCHER)
        assert card.capabilities == []
        assert card.description == ""
        assert card.endpoint is None
        assert card.metadata == {}


class TestDispatchedTask:
    def test_initial_state(self):
        task = DispatchedTask(
            task_id="t1",
            agent_id="a1",
            description="build module",
        )
        assert task.status == TaskStatus.PENDING
        assert task.assigned_at is None
        assert task.result is None

    def test_assign(self):
        task = DispatchedTask(task_id="t1", agent_id="a1", description="task")
        task.assign()
        assert task.status == TaskStatus.ASSIGNED
        assert task.assigned_at is not None

    def test_start(self):
        task = DispatchedTask(task_id="t1", agent_id="a1", description="task")
        task.assign()
        task.start()
        assert task.status == TaskStatus.IN_PROGRESS

    def test_complete(self):
        task = DispatchedTask(task_id="t1", agent_id="a1", description="task")
        task.assign()
        task.complete({"output": "done"})
        assert task.status == TaskStatus.COMPLETED
        assert task.result == {"output": "done"}
        assert task.completed_at is not None

    def test_fail(self):
        task = DispatchedTask(task_id="t1", agent_id="a1", description="task")
        task.assign()
        task.fail("something went wrong")
        assert task.status == TaskStatus.FAILED
        assert task.error == "something went wrong"


class TestTaskDispatch:
    def test_register_agent(self):
        dispatch = TaskDispatch()
        card = AgentCard(agent_id="a1", role=AgentRole.BUILDER)
        dispatch.register_agent(card)
        assert "a1" in dispatch.agents

    def test_unregister_agent(self):
        dispatch = TaskDispatch()
        card = AgentCard(agent_id="a1", role=AgentRole.BUILDER)
        dispatch.register_agent(card)
        removed = dispatch.unregister_agent("a1")
        assert removed.agent_id == "a1"
        assert "a1" not in dispatch.agents

    def test_unregister_nonexistent(self):
        dispatch = TaskDispatch()
        assert dispatch.unregister_agent("nonexistent") is None

    def test_assign_by_role(self):
        dispatch = TaskDispatch()
        dispatch.register_agent(AgentCard(agent_id="b1", role=AgentRole.BUILDER))
        dispatch.register_agent(AgentCard(agent_id="r1", role=AgentRole.REVIEWER))

        task = dispatch.assign("t1", "build x", required_role=AgentRole.BUILDER)
        assert task is not None
        assert task.agent_id == "b1"

    def test_assign_no_matching_role_fallback(self):
        dispatch = TaskDispatch()
        dispatch.register_agent(AgentCard(agent_id="b1", role=AgentRole.BUILDER))

        task = dispatch.assign("t1", "review x", required_role=AgentRole.REVIEWER)
        assert task is not None
        assert task.agent_id == "b1"

    def test_assign_no_agents(self):
        dispatch = TaskDispatch()
        task = dispatch.assign("t1", "do x")
        assert task is None

    def test_assign_to_capable(self):
        dispatch = TaskDispatch()
        dispatch.register_agent(
            AgentCard(
                agent_id="b1",
                role=AgentRole.BUILDER,
                capabilities=["python"],
            )
        )
        dispatch.register_agent(
            AgentCard(
                agent_id="b2",
                role=AgentRole.BUILDER,
                capabilities=["rust"],
            )
        )

        task = dispatch.assign_to_capable("t1", "write rust", required_capability="rust")
        assert task is not None
        assert task.agent_id == "b2"

    def test_assign_to_capable_no_match(self):
        dispatch = TaskDispatch()
        dispatch.register_agent(AgentCard(agent_id="a1", role=AgentRole.BUILDER, capabilities=["python"]))

        task = dispatch.assign_to_capable("t1", "write rust", required_capability="rust")
        assert task is None

    def test_get_agent(self):
        dispatch = TaskDispatch()
        card = AgentCard(agent_id="a1", role=AgentRole.BUILDER)
        dispatch.register_agent(card)
        assert dispatch.get_agent("a1") is card
        assert dispatch.get_agent("nonexistent") is None

    def test_list_by_role(self):
        dispatch = TaskDispatch()
        dispatch.register_agent(AgentCard(agent_id="b1", role=AgentRole.BUILDER))
        dispatch.register_agent(AgentCard(agent_id="b2", role=AgentRole.BUILDER))
        dispatch.register_agent(AgentCard(agent_id="r1", role=AgentRole.REVIEWER))

        builders = dispatch.list_by_role(AgentRole.BUILDER)
        assert len(builders) == 2


class TestResultMerge:
    def test_empty_results(self):
        merge = ResultMerge(strategy=MergeStrategy.VOTE)
        result = merge.merge([])
        assert result["merged"] is True
        assert result["results"] == []

    def test_vote_strategy(self):
        merge = ResultMerge(strategy=MergeStrategy.VOTE)
        result = merge.merge(
            [
                {"answer": "A"},
                {"answer": "A"},
                {"answer": "B"},
            ]
        )
        assert result["strategy"] == "vote"
        assert result["winner"] == "A"
        assert result["vote_count"] == 2
        assert result["total_votes"] == 3

    def test_vote_with_result_key(self):
        merge = ResultMerge(strategy=MergeStrategy.VOTE)
        result = merge.merge(
            [
                {"result": "X"},
                {"result": "Y"},
                {"result": "X"},
            ]
        )
        assert result["winner"] == "X"

    def test_chain_strategy(self):
        merge = ResultMerge(strategy=MergeStrategy.CHAIN)
        result = merge.merge(
            [
                {"result": "step1", "context": {"a": 1}},
                {"result": "step2", "context": {"b": 2}},
            ]
        )
        assert result["strategy"] == "chain"
        assert result["outputs"] == ["step1", "step2"]
        assert result["context"] == {"a": 1, "b": 2}

    def test_consensus_reached(self):
        merge = ResultMerge(strategy=MergeStrategy.CONSENSUS)
        result = merge.merge(
            [
                {"result": "agree"},
                {"result": "agree"},
                {"result": "agree"},
            ]
        )
        assert result["consensus_reached"] is True
        assert result["result"] == "agree"
        assert result["disagreements"] == 0

    def test_consensus_not_reached(self):
        merge = ResultMerge(strategy=MergeStrategy.CONSENSUS)
        result = merge.merge(
            [
                {"result": "A"},
                {"result": "B"},
                {"result": "C"},
            ]
        )
        assert result["consensus_reached"] is False
        assert result["result"] is None
        assert result["disagreements"] == 2
        assert result["total"] == 3


class TestDefaultMergeStrategy:
    def test_default_is_consensus(self):
        merge = ResultMerge()
        assert merge.strategy == MergeStrategy.CONSENSUS
