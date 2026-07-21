# [A_test] module_id: MOD-GOV_a2a_state | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §
# [MODULE] tests.test_a2a_state
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_a2a_state.py
# [TTL] task_bound

import pytest

from zephyr.infrastructure.a2a_protocol.layer2_communication.a2a_state import (
    A2AStateMachine,
    A2ATask,
    A2ATaskStatus,
)


class TestA2ATaskStatus:
    def test_enum_values(self):
        assert A2ATaskStatus.CREATED == "created"
        assert A2ATaskStatus.QUEUED == "queued"
        assert A2ATaskStatus.ASSIGNED == "assigned"
        assert A2ATaskStatus.IN_PROGRESS == "in_progress"
        assert A2ATaskStatus.WAITING_REVIEW == "waiting_review"
        assert A2ATaskStatus.COMPLETED == "completed"
        assert A2ATaskStatus.FAILED == "failed"
        assert A2ATaskStatus.CANCELLED == "cancelled"
        assert A2ATaskStatus.TIMEOUT == "timeout"


class TestA2ATask:
    def test_create_valid_task(self):
        task = A2ATask(
            task_id="a2a-task-001",
            from_agent="agent-a",
            description="do something",
        )
        assert task.task_id == "a2a-task-001"
        assert task.status == A2ATaskStatus.CREATED
        assert task.to_agent is None
        assert task.retry_count == 0
        assert task.max_retries == 3

    def test_invalid_task_id(self):
        with pytest.raises(Exception):
            A2ATask(task_id="bad-id", from_agent="a", description="x")

    def test_with_optional_fields(self):
        task = A2ATask(
            task_id="a2a-task-002",
            from_agent="a",
            description="x",
            to_agent="agent-b",
            context_ref="ctx-1",
            max_retries=5,
        )
        assert task.to_agent == "agent-b"
        assert task.context_ref == "ctx-1"
        assert task.max_retries == 5


class TestA2AStateMachine:
    def test_valid_transition_created_to_queued(self):
        task = A2ATask(task_id="a2a-task-010", from_agent="a", description="x")
        result = A2AStateMachine.transition(task, A2ATaskStatus.QUEUED)
        assert result is True
        assert task.status == A2ATaskStatus.QUEUED

    def test_valid_transition_queued_to_assigned(self):
        task = A2ATask(task_id="a2a-task-011", from_agent="a", description="x")
        A2AStateMachine.transition(task, A2ATaskStatus.QUEUED)
        result = A2AStateMachine.transition(task, A2ATaskStatus.ASSIGNED)
        assert result is True
        assert task.status == A2ATaskStatus.ASSIGNED

    def test_invalid_transition_created_to_completed(self):
        task = A2ATask(task_id="a2a-task-012", from_agent="a", description="x")
        result = A2AStateMachine.transition(task, A2ATaskStatus.COMPLETED)
        assert result is False
        assert task.status == A2ATaskStatus.CREATED

    def test_failed_to_queued_retry(self):
        task = A2ATask(task_id="a2a-task-013", from_agent="a", description="x")
        A2AStateMachine.transition(task, A2ATaskStatus.QUEUED)
        A2AStateMachine.transition(task, A2ATaskStatus.ASSIGNED)
        A2AStateMachine.transition(task, A2ATaskStatus.IN_PROGRESS)
        A2AStateMachine.transition(task, A2ATaskStatus.FAILED)
        result = A2AStateMachine.transition(task, A2ATaskStatus.QUEUED)
        assert result is True
        assert task.status == A2ATaskStatus.QUEUED

    def test_transition_updates_timestamp(self):
        task = A2ATask(task_id="a2a-task-014", from_agent="a", description="x")
        old_updated = task.updated_at
        A2AStateMachine.transition(task, A2ATaskStatus.QUEUED)
        assert task.updated_at >= old_updated
