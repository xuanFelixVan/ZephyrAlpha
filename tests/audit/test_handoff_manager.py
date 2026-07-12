# [A_test] module_id: SRC-TST-1090 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §
# [MODULE] tests.test_handoff_manager
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_handoff_manager.py
# [TTL] task_bound

from zephyr.gov_drift.handoff_manager import (
    HandoffManager,
    HandoffRecord,
)


class TestHandoffRecord:
    def test_create(self):
        rec = HandoffRecord(from_agent="a", to_agent="b", task_id="t1", reason="shift")
        assert rec.from_agent == "a"
        assert rec.to_agent == "b"
        assert rec.task_id == "t1"
        assert rec.reason == "shift"
        assert rec.acknowledged is False

    def test_to_dict(self):
        rec = HandoffRecord(from_agent="a", to_agent="b", task_id="t1", reason="shift")
        d = rec.to_dict()
        assert d["from"] == "a"
        assert d["to"] == "b"
        assert d["task_id"] == "t1"
        assert d["reason"] == "shift"
        assert d["acknowledged"] is False
        assert "timestamp" in d


class TestHandoffManager:
    def test_create(self):
        mgr = HandoffManager()
        assert mgr.get_active_handoffs() == []

    def test_handoff_creates_record(self):
        mgr = HandoffManager()
        rec = mgr.handoff("agent-a", "agent-b", "task-1", "reassignment")
        assert rec.from_agent == "agent-a"
        assert rec.to_agent == "agent-b"
        assert rec.acknowledged is False
        assert len(mgr.get_active_handoffs()) == 1

    def test_acknowledge_handoff(self):
        mgr = HandoffManager()
        mgr.handoff("agent-a", "agent-b", "task-1", "reassignment")
        result = mgr.acknowledge("agent-b", "task-1")
        assert result is True
        assert len(mgr.get_active_handoffs()) == 0

    def test_acknowledge_nonexistent(self):
        mgr = HandoffManager()
        result = mgr.acknowledge("agent-x", "task-999")
        assert result is False

    def test_multiple_handoffs(self):
        mgr = HandoffManager()
        mgr.handoff("a", "b", "t1", "r1")
        mgr.handoff("b", "c", "t2", "r2")
        assert len(mgr.get_active_handoffs()) == 2
        mgr.acknowledge("b", "t1")
        assert len(mgr.get_active_handoffs()) == 1

    def test_acknowledge_only_latest(self):
        mgr = HandoffManager()
        mgr.handoff("a", "b", "t1", "r1")
        mgr.handoff("a", "b", "t1", "r2")
        mgr.acknowledge("b", "t1")
        assert len(mgr.get_active_handoffs()) == 1
