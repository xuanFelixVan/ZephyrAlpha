"""测试: A2A Task 状态机"""

import pytest
from zephyr.l01_infrastructure.a2a_protocol.layer2_communication.a2a_state import (
    A2ATask, A2ATaskStatus, A2AStateMachine,
)


class TestA2AStateMachine:
    def test_create_task(self):
        task = A2ATask(task_id="a2a-task-test-001", from_agent="agent-x", description="Test")
        assert task.status == A2ATaskStatus.CREATED

    def test_valid_transition(self):
        task = A2ATask(task_id="a2a-task-test-002", from_agent="agent-x", description="Test")
        assert A2AStateMachine.transition(task, A2ATaskStatus.QUEUED)
        assert task.status == A2ATaskStatus.QUEUED

    def test_invalid_transition(self):
        task = A2ATask(task_id="a2a-task-test-003", from_agent="agent-x", description="Test")
        assert not A2AStateMachine.transition(task, A2ATaskStatus.IN_PROGRESS)
        assert task.status == A2ATaskStatus.CREATED
