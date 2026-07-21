# [A_test] module_id: MOD-GOV_e_deadlock_detector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_deadlock_detector
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.resilience_governance.deadlock_detector import DeadlockDetector


class TestDeadlockDetectorInit:
    def test_empty_state(self):
        dd = DeadlockDetector()
        assert dd._wait_graph == {}
        assert dd._locks == {}
        assert dd._preemption_order == []


class TestDeadlockDetectorAddEdge:
    def test_single_edge(self):
        dd = DeadlockDetector()
        dd.add_edge("agent-1", "agent-2")
        assert dd._wait_graph == {"agent-1": {"agent-2"}}

    def test_multiple_edges(self):
        dd = DeadlockDetector()
        dd.add_edge("a", "b")
        dd.add_edge("a", "c")
        assert dd._wait_graph["a"] == {"b", "c"}


class TestDeadlockDetectorDetectCycle:
    def test_no_cycle(self):
        dd = DeadlockDetector()
        dd.add_edge("a", "b")
        dd.add_edge("b", "c")
        assert dd.detect_cycle() == []

    def test_simple_cycle(self):
        dd = DeadlockDetector()
        dd.add_edge("a", "b")
        dd.add_edge("b", "a")
        assert len(dd.detect_cycle()) > 0

    def test_three_node_cycle(self):
        dd = DeadlockDetector()
        dd.add_edge("a", "b")
        dd.add_edge("b", "c")
        dd.add_edge("c", "a")
        cycle = dd.detect_cycle()
        assert len(cycle) > 0

    def test_empty_graph_no_cycle(self):
        dd = DeadlockDetector()
        assert dd.detect_cycle() == []


class TestDeadlockDetectorBreakDeadlock:
    def test_removes_node(self):
        dd = DeadlockDetector()
        dd.add_edge("a", "b")
        result = dd.break_deadlock("a")
        assert result is True
        assert "a" not in dd._wait_graph

    def test_nonexistent_node(self):
        dd = DeadlockDetector()
        result = dd.break_deadlock("x")
        assert result is True


class TestDeadlockDetectorAcquireRelease:
    def test_try_acquire_success(self):
        dd = DeadlockDetector()
        assert dd.try_acquire("resource-1", "agent-1") is True
        assert dd._locks["resource-1"] == "agent-1"

    def test_try_acquire_already_held(self):
        dd = DeadlockDetector()
        dd.try_acquire("r1", "agent-1")
        assert dd.try_acquire("r1", "agent-2") is False

    def test_release_correct_holder(self):
        dd = DeadlockDetector()
        dd.try_acquire("r1", "agent-1")
        assert dd.release("r1", "agent-1") is True
        assert "r1" not in dd._locks

    def test_release_wrong_holder(self):
        dd = DeadlockDetector()
        dd.try_acquire("r1", "agent-1")
        assert dd.release("r1", "agent-2") is False
        assert "r1" in dd._locks


class TestDeadlockDetectorSerialize:
    def test_serialize_empty(self):
        dd = DeadlockDetector()
        data = dd.serialize()
        assert data["wait_graph"] == {}
        assert data["locks"] == {}
        assert data["preemption_order"] == []

    def test_serialize_with_data(self):
        dd = DeadlockDetector()
        dd.add_edge("a", "b")
        dd.try_acquire("r1", "agent-1")
        data = dd.serialize()
        assert data["wait_graph"]["a"] == ["b"]
        assert data["locks"]["r1"] == "agent-1"
