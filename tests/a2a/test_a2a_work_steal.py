# [A_test] module_id: MOD-GOV_a2a_work_steal | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §
# [MODULE] tests.test_a2a_work_steal
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_a2a_work_steal.py
# [TTL] task_bound

from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_work_steal import (
    A2AWorkSteal,
    TaskQueue,
)


class TestTaskQueue:
    def test_create(self):
        tq = TaskQueue(agent_id="agent-a")
        assert tq.load == 0
        assert tq.has_spare_capacity is True

    def test_add_task(self):
        tq = TaskQueue(agent_id="agent-a")
        tq.add({"task_id": "t1", "priority": 1})
        assert tq.load == 1

    def test_add_beyond_max(self):
        tq = TaskQueue(agent_id="agent-a", max_queue=2)
        tq.add({"task_id": "t1"})
        tq.add({"task_id": "t2"})
        tq.add({"task_id": "t3"})
        assert tq.load == 2

    def test_remove_task(self):
        tq = TaskQueue(agent_id="agent-a")
        tq.add({"task_id": "t1"})
        removed = tq.remove("t1")
        assert removed is not None
        assert removed["task_id"] == "t1"
        assert tq.load == 0

    def test_remove_nonexistent(self):
        tq = TaskQueue(agent_id="agent-a")
        assert tq.remove("missing") is None


class TestA2AWorkSteal:
    def test_create_default(self):
        ws = A2AWorkSteal()
        assert ws._max_steal_per_cycle == 3

    def test_steal_from_busy_agent(self):
        ws = A2AWorkSteal(steal_threshold=1)
        busy = TaskQueue(agent_id="busy-agent")
        for i in range(5):
            busy.add({"task_id": f"t{i}", "priority": i})
        idle = TaskQueue(agent_id="idle-agent")
        queues = {"busy-agent": busy, "idle-agent": idle}
        stolen = ws.steal("idle-agent", queues)
        assert len(stolen) > 0
        assert stolen[0].get("stolen_by") == "idle-agent"

    def test_steal_no_busy_agents(self):
        ws = A2AWorkSteal(steal_threshold=5)
        q1 = TaskQueue(agent_id="a")
        q2 = TaskQueue(agent_id="b")
        queues = {"a": q1, "b": q2}
        stolen = ws.steal("a", queues)
        assert stolen == []

    def test_steal_idle_agent_full(self):
        ws = A2AWorkSteal(steal_threshold=1)
        busy = TaskQueue(agent_id="busy")
        busy.add({"task_id": "t1", "priority": 1})
        full = TaskQueue(agent_id="idle", max_queue=0)
        queues = {"busy": busy, "idle": full}
        stolen = ws.steal("idle", queues)
        assert stolen == []

    def test_steal_respects_max_per_cycle(self):
        ws = A2AWorkSteal(max_steal_per_cycle=1, steal_threshold=1)
        busy = TaskQueue(agent_id="busy")
        for i in range(5):
            busy.add({"task_id": f"t{i}", "priority": i})
        idle = TaskQueue(agent_id="idle")
        queues = {"busy": busy, "idle": idle}
        stolen = ws.steal("idle", queues)
        assert len(stolen) <= 1

    def test_steal_nonexistent_idle_agent(self):
        ws = A2AWorkSteal()
        queues = {"busy": TaskQueue(agent_id="busy")}
        stolen = ws.steal("missing", queues)
        assert stolen == []

    def test_no_duplicate_steal(self):
        ws = A2AWorkSteal(max_steal_per_cycle=10, steal_threshold=1)
        busy = TaskQueue(agent_id="busy")
        for i in range(3):
            busy.add({"task_id": f"t{i}", "priority": i})
        idle = TaskQueue(agent_id="idle")
        queues = {"busy": busy, "idle": idle}
        stolen1 = ws.steal("idle", queues)
        assert len(stolen1) >= 1
        for t in stolen1:
            assert ws._stolen.__contains__(t.get("task_id", ""))
