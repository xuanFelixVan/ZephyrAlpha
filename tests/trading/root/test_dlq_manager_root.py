# [A_test] module_id: SRC-TST-0757 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_dlq_manager
# [INVARIANTS] DLQManager uses in-memory dict; max_attempts=3 by default
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_dlq_manager_root.py
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime

from zephyr.orchestrator.execution.dlq_manager import DLQManager, DLQMessage


class TestDLQMessage:
    def test_default_values(self):
        msg = DLQMessage(message_id="m1", contract_id="c1")
        assert msg.message_id == "m1"
        assert msg.contract_id == "c1"
        assert msg.payload == {}
        assert msg.attempt_count == 0
        assert msg.max_attempts == 3
        assert msg.status == "pending"
        assert msg.last_attempt_at is None

    def test_custom_values(self):
        now = datetime.now(UTC)
        msg = DLQMessage(
            message_id="m1",
            contract_id="c1",
            payload={"key": "val"},
            attempt_count=1,
            max_attempts=5,
            status="completed",
            enqueued_at=now,
        )
        assert msg.payload == {"key": "val"}
        assert msg.attempt_count == 1
        assert msg.max_attempts == 5
        assert msg.status == "completed"


class TestDLQManagerEnqueue:
    def test_enqueue_returns_message(self):
        mgr = DLQManager()
        msg = mgr.enqueue("m1", "c1")
        assert isinstance(msg, DLQMessage)
        assert msg.message_id == "m1"
        assert msg.contract_id == "c1"
        assert msg.status == "pending"

    def test_enqueue_with_payload(self):
        mgr = DLQManager()
        msg = mgr.enqueue("m1", "c1", payload={"error": "timeout"})
        assert msg.payload == {"error": "timeout"}

    def test_enqueue_with_none_payload(self):
        mgr = DLQManager()
        msg = mgr.enqueue("m1", "c1", payload=None)
        assert msg.payload == {}

    def test_enqueue_overwrites_same_id(self):
        mgr = DLQManager()
        mgr.enqueue("m1", "c1")
        mgr.enqueue("m1", "c2")
        all_msgs = mgr.list_all()
        assert len(all_msgs) == 1
        assert all_msgs[0].contract_id == "c2"


class TestDLQManagerPeek:
    def test_peek_returns_oldest_pending(self):
        mgr = DLQManager()
        mgr.enqueue("m1", "c1")
        mgr.enqueue("m2", "c2")
        msg = mgr.peek()
        assert msg is not None
        assert msg.message_id == "m1"

    def test_peek_empty_returns_none(self):
        mgr = DLQManager()
        assert mgr.peek() is None

    def test_peek_skips_non_pending(self):
        mgr = DLQManager()
        mgr.enqueue("m1", "c1")
        mgr.replay("m1")
        assert mgr.peek() is None


class TestDLQManagerReplay:
    def test_replay_success(self):
        mgr = DLQManager()
        mgr.enqueue("m1", "c1")
        ok, reason = mgr.replay("m1")
        assert ok is True
        assert reason == "SUCCESS"
        msg = mgr.list_all()[0]
        assert msg.status == "completed"
        assert msg.attempt_count == 1
        assert msg.last_attempt_at is not None

    def test_replay_not_found(self):
        mgr = DLQManager()
        ok, reason = mgr.replay("nonexistent")
        assert ok is False
        assert reason == "NOT_FOUND"

    def test_replay_max_attempts_exceeded(self):
        mgr = DLQManager()
        mgr.enqueue("m1", "c1")
        mgr.replay("m1")
        mgr._messages["m1"].status = "pending"
        mgr.replay("m1")
        mgr._messages["m1"].status = "pending"
        mgr.replay("m1")
        mgr._messages["m1"].status = "pending"
        ok, reason = mgr.replay("m1")
        assert ok is False
        assert reason == "MAX_ATTEMPTS_EXCEEDED"
        msg = mgr._messages["m1"]
        assert msg.status == "dead"
        assert msg.attempt_count == 4

    def test_replay_increments_attempt_count(self):
        mgr = DLQManager()
        mgr.enqueue("m1", "c1")
        mgr.replay("m1")
        assert mgr._messages["m1"].attempt_count == 1


class TestDLQManagerListAll:
    def test_list_all_empty(self):
        mgr = DLQManager()
        assert mgr.list_all() == []

    def test_list_all_returns_all(self):
        mgr = DLQManager()
        mgr.enqueue("m1", "c1")
        mgr.enqueue("m2", "c2")
        all_msgs = mgr.list_all()
        assert len(all_msgs) == 2


class TestDLQManagerListDead:
    def test_list_dead_empty(self):
        mgr = DLQManager()
        assert mgr.list_dead() == []

    def test_list_dead_returns_only_dead(self):
        mgr = DLQManager()
        mgr.enqueue("m1", "c1")
        mgr.enqueue("m2", "c2")
        mgr.replay("m1")
        mgr._messages["m1"].status = "pending"
        mgr.replay("m1")
        mgr._messages["m1"].status = "pending"
        mgr.replay("m1")
        mgr._messages["m1"].status = "pending"
        mgr.replay("m1")
        dead = mgr.list_dead()
        assert len(dead) == 1
        assert dead[0].message_id == "m1"

    def test_list_dead_excludes_pending(self):
        mgr = DLQManager()
        mgr.enqueue("m1", "c1")
        assert mgr.list_dead() == []
