# [A_test] module_id: SRC-TST-0710 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain-autonomy_core/rollback-system/blueprint.md | §
# [MODULE] tests.test_deadlock_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_deadlock_detector.py -q

from __future__ import annotations

from zephyr.governance.deadlock_detector import DeadlockDetector


class TestDeadlockDetectorInstantiation:
    def test_creates_instance_without_args(self):
        det = DeadlockDetector()
        assert isinstance(det, DeadlockDetector)

    def test_initial_wait_graph_empty(self):
        det = DeadlockDetector()
        assert det._wait_graph == {}

    def test_initial_locks_empty(self):
        det = DeadlockDetector()
        assert det._locks == {}

    def test_initial_preemption_order_empty(self):
        det = DeadlockDetector()
        assert det._preemption_order == []


class TestAddEdge:
    def test_add_single_edge(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        assert "B" in det._wait_graph["A"]

    def test_add_multiple_edges_same_waiter(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        det.add_edge("A", "C")
        assert det._wait_graph["A"] == {"B", "C"}

    def test_add_duplicate_edge_no_duplication(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        det.add_edge("A", "B")
        assert det._wait_graph["A"] == {"B"}


class TestDetectCycle:
    def test_no_cycle_returns_empty(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        det.add_edge("B", "C")
        result = det.detect_cycle()
        assert result == []

    def test_simple_cycle_detected(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        det.add_edge("B", "A")
        result = det.detect_cycle()
        assert len(result) > 0

    def test_three_node_cycle_detected(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        det.add_edge("B", "C")
        det.add_edge("C", "A")
        result = det.detect_cycle()
        assert len(result) > 0

    def test_empty_graph_returns_empty(self):
        det = DeadlockDetector()
        result = det.detect_cycle()
        assert result == []

    def test_self_loop_detected(self):
        det = DeadlockDetector()
        det.add_edge("A", "A")
        result = det.detect_cycle()
        assert len(result) > 0


class TestBreakDeadlock:
    def test_removes_node_from_graph(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        det.add_edge("B", "A")
        result = det.break_deadlock("A")
        assert result is True
        assert "A" not in det._wait_graph

    def test_nonexistent_node_returns_true(self):
        det = DeadlockDetector()
        result = det.break_deadlock("Z")
        assert result is True

    def test_breaking_node_resolves_cycle(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        det.add_edge("B", "C")
        det.add_edge("C", "A")
        det.break_deadlock("C")
        result = det.detect_cycle()
        assert result == []


class TestTryAcquire:
    def test_acquire_free_resource(self):
        det = DeadlockDetector()
        result = det.try_acquire("res1", "holder1")
        assert result is True
        assert det._locks["res1"] == "holder1"

    def test_acquire_locked_resource_fails(self):
        det = DeadlockDetector()
        det.try_acquire("res1", "holder1")
        result = det.try_acquire("res1", "holder2")
        assert result is False

    def test_same_holder_cannot_double_acquire(self):
        det = DeadlockDetector()
        det.try_acquire("res1", "holder1")
        result = det.try_acquire("res1", "holder1")
        assert result is False


class TestRelease:
    def test_release_by_owner_succeeds(self):
        det = DeadlockDetector()
        det.try_acquire("res1", "holder1")
        result = det.release("res1", "holder1")
        assert result is True
        assert "res1" not in det._locks

    def test_release_by_non_owner_fails(self):
        det = DeadlockDetector()
        det.try_acquire("res1", "holder1")
        result = det.release("res1", "holder2")
        assert result is False
        assert det._locks["res1"] == "holder1"

    def test_release_nonexistent_resource_fails(self):
        det = DeadlockDetector()
        result = det.release("res1", "holder1")
        assert result is False

    def test_acquire_after_release_succeeds(self):
        det = DeadlockDetector()
        det.try_acquire("res1", "holder1")
        det.release("res1", "holder1")
        result = det.try_acquire("res1", "holder2")
        assert result is True


class TestDijkstraOrder:
    def test_linear_chain_contains_all_nodes(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        det.add_edge("B", "C")
        order = det.dijkstra_order()
        assert set(order) == {"A", "B", "C"}

    def test_empty_graph_returns_empty(self):
        det = DeadlockDetector()
        order = det.dijkstra_order()
        assert order == []

    def test_single_node(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        order = det.dijkstra_order()
        assert set(order) == {"A", "B"}

    def test_sets_preemption_order(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        det.dijkstra_order()
        assert len(det._preemption_order) > 0


class TestPreemptLowest:
    def test_preempts_from_order(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        det.add_edge("B", "C")
        det.dijkstra_order()
        victim = det.preempt_lowest()
        assert victim is not None

    def test_empty_graph_returns_none(self):
        det = DeadlockDetector()
        result = det.preempt_lowest()
        assert result is None

    def test_preempt_removes_from_graph(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        det.add_edge("B", "C")
        det.dijkstra_order()
        victim = det.preempt_lowest()
        assert victim not in det._wait_graph

    def test_preempt_auto_computes_order(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        victim = det.preempt_lowest()
        assert victim is not None


class TestSerialize:
    def test_serialize_empty(self):
        det = DeadlockDetector()
        result = det.serialize()
        assert result["wait_graph"] == {}
        assert result["locks"] == {}
        assert result["preemption_order"] == []

    def test_serialize_with_data(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        det.try_acquire("res1", "holder1")
        result = det.serialize()
        assert "A" in result["wait_graph"]
        assert "B" in result["wait_graph"]["A"]
        assert result["locks"]["res1"] == "holder1"

    def test_serialize_wait_graph_values_are_lists(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        det.add_edge("A", "C")
        result = det.serialize()
        assert isinstance(result["wait_graph"]["A"], list)
        assert set(result["wait_graph"]["A"]) == {"B", "C"}
