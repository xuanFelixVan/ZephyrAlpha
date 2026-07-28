# [A_test] module_id: MOD-GOV_supervisor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §
# [MODULE] tests.test_supervisor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_supervisor.py
# [TTL] task_bound

from datetime import datetime, timedelta

from zephyr.infrastructure.a2a_protocol.layer2_communication.a2a_state import (
    A2ATask,
    A2ATaskStatus,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.supervisor import Supervisor


def _make_task(task_id="a2a-task-sup-1", status=A2ATaskStatus.QUEUED, to_agent=None, deadline=None):
    return A2ATask(
        task_id=task_id,
        from_agent="agent-a",
        description="test task",
        status=status,
        to_agent=to_agent,
        deadline=deadline,
    )


class TestSupervisor:
    def test_create(self):
        sv = Supervisor()
        assert sv.tasks == {}

    def test_submit_task(self):
        sv = Supervisor()
        task = _make_task()
        result = sv.submit_task(task)
        assert result.task_id in sv.tasks
        assert result.deadline is not None

    def test_submit_task_deadline_clamped_min(self):
        sv = Supervisor()
        task = _make_task(deadline=datetime.utcnow() + timedelta(seconds=30))
        result = sv.submit_task(task)
        min_dl = datetime.utcnow() + timedelta(minutes=sv.MIN_TIMEOUT_MINUTES)
        assert result.deadline >= min_dl - timedelta(seconds=1)

    def test_assign_task(self):
        sv = Supervisor()
        task = _make_task()
        sv.submit_task(task)
        result = sv.assign_task("a2a-task-sup-1", "agent-b")
        assert result is True
        assert sv.tasks["a2a-task-sup-1"].status == A2ATaskStatus.ASSIGNED

    def test_assign_nonexistent_task(self):
        sv = Supervisor()
        result = sv.assign_task("missing", "agent-b")
        assert result is False

    def test_get_agent_load(self):
        sv = Supervisor()
        task = _make_task(to_agent="agent-b")
        sv.submit_task(task)
        assert sv.get_agent_load("agent-b") == 1
        assert sv.get_agent_load("agent-x") == 0

    def test_get_pending_tasks(self):
        sv = Supervisor()
        sv.submit_task(_make_task("a2a-task-sup-p1", A2ATaskStatus.CREATED))
        sv.submit_task(_make_task("a2a-task-sup-p2", A2ATaskStatus.QUEUED))
        pending = sv.get_pending_tasks()
        assert len(pending) == 2

    def test_escalate_timeouts(self):
        sv = Supervisor()
        task = _make_task()
        sv.submit_task(task)
        sv.tasks["a2a-task-sup-1"].deadline = datetime.utcnow() - timedelta(hours=1)
        timeouts = sv.escalate_timeouts()
        assert len(timeouts) > 0
        assert sv.tasks["a2a-task-sup-1"].status == A2ATaskStatus.TIMEOUT

    def test_detect_deadlocks_no_deadlock(self):
        sv = Supervisor()
        task = _make_task(deadline=datetime.utcnow() + timedelta(hours=1))
        task.status = A2ATaskStatus.IN_PROGRESS
        sv.submit_task(task)
        deadlocks = sv.detect_deadlocks()
        assert deadlocks == []
