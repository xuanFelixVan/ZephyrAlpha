# [A_test] module_id: SRC-TST-2010 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-627 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_dlq_manager
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""DLQ 管理器单元测试——enqueue + replay + max_attempts。"""


import pytest

from zephyr.orchestrator.execution.dlq_manager import DLQManager


@pytest.fixture
def dlq():
    return DLQManager()


def test_enqueue_message(dlq):
    msg = dlq.enqueue("MSG-001", "CT-ORC-CE-001")
    assert msg.message_id == "MSG-001"
    assert msg.status == "pending"


def test_peek_returns_oldest(dlq):
    dlq.enqueue("MSG-A", "CT-ORC-CE-001")
    dlq.enqueue("MSG-B", "CT-ORC-CE-001")
    peeked = dlq.peek()
    assert peeked.message_id == "MSG-A"


def test_replay_success(dlq):
    dlq.enqueue("MSG-001", "CT-ORC-CE-001")
    ok, status = dlq.replay("MSG-001")
    assert ok is True
    assert status == "SUCCESS"


def test_replay_max_attempts_exceeded(dlq):
    dlq.enqueue("MSG-001", "CT-ORC-CE-001")
    for _ in range(3):
        dlq.replay("MSG-001")
    ok, status = dlq.replay("MSG-001")
    assert ok is False
    assert status == "MAX_ATTEMPTS_EXCEEDED"
    assert "MSG-001" in [m.message_id for m in dlq.list_dead()]
