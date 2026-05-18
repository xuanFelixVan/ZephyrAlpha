# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_supervisor
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: Supervisor"""

import pytest
from datetime import datetime, timedelta
from zephyr.l01_infrastructure.a2a_protocol.layer2_communication.a2a_state import A2ATask, A2ATaskStatus
from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.supervisor import Supervisor


class TestSupervisor:
    def test_submit_task(self):
        sup = Supervisor()
        task = A2ATask(task_id="a2a-task-s-001", from_agent="agent-x", description="test")
        sup.submit_task(task)
        assert "a2a-task-s-001" in sup._tasks
        assert task.deadline is not None

    def test_assign_task(self):
        sup = Supervisor()
        task = A2ATask(task_id="a2a-task-s-002", from_agent="agent-x", description="test")
        sup.submit_task(task)
        A2ATaskStatus.QUEUED  # transition needed
        task.status = A2ATaskStatus.QUEUED
        assert sup.assign_task("a2a-task-s-002", "agent-worker")
        assert task.to_agent == "agent-worker"

    def test_detect_deadlines_past(self):
        sup = Supervisor()
        task = A2ATask(task_id="a2a-task-s-003", from_agent="agent-x", description="test")
        task.status = A2ATaskStatus.IN_PROGRESS
        task.to_agent = "agent-worker"
        task.deadline = datetime.utcnow() - timedelta(minutes=1)
        sup._tasks[task.task_id] = task
        deadlocks = sup.detect_deadlocks()
        assert len(deadlocks) == 1
