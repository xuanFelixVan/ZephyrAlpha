# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_work_steal
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: WorkSteal"""

from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_work_steal import (
    A2AWorkSteal,
    TaskQueue,
)


def test_steal_from_busy_agent():
    ws = A2AWorkSteal(steal_threshold=1)
    busy_queue = TaskQueue(agent_id="busy-agent")
    busy_queue.add({"task_id": "t1", "priority": 1})
    busy_queue.add({"task_id": "t2", "priority": 2})
    busy_queue.add({"task_id": "t3", "priority": 0})
    idle_queue = TaskQueue(agent_id="idle-agent")
    queues = {"busy-agent": busy_queue, "idle-agent": idle_queue}
    stolen = ws.steal("idle-agent", queues)
    assert len(stolen) > 0
    assert stolen[0]["stolen_by"] == "idle-agent"


def test_no_steal_when_all_idle():
    ws = A2AWorkSteal()
    q1 = TaskQueue(agent_id="a1")
    q2 = TaskQueue(agent_id="a2")
    queues = {"a1": q1, "a2": q2}
    stolen = ws.steal("a1", queues)
    assert stolen == []


def test_task_queue_add_and_remove():
    q = TaskQueue(agent_id="test")
    q.add({"task_id": "t1"})
    q.add({"task_id": "t2"})
    assert q.load == 2
    removed = q.remove("t1")
    assert removed is not None
    assert removed["task_id"] == "t1"
    assert q.load == 1


def test_task_queue_max():
    q = TaskQueue(agent_id="test", max_queue=2)
    q.add({"task_id": "t1"})
    q.add({"task_id": "t2"})
    q.add({"task_id": "t3"})
    assert q.load == 2


def test_task_queue_spare_capacity():
    q = TaskQueue(agent_id="test", max_queue=5)
    q.add({"task_id": "t1"})
    assert q.has_spare_capacity
