# [A_test] module_id: MOD-GOV_deadlock_detector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_deadlock_detector
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_deadlock_detector.py -q
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.resilience_governance.deadlock_detector import DeadlockDetector


class TestDeadlockDetectorInstantiation:
    def test_creates_instance_without_args(self):
        det = DeadlockDetector()
        assert isinstance(det, DeadlockDetector)

    def test_initial_wait_graph_empty(self):
        det = DeadlockDetector()
        assert det.wait_graph == {}

    def test_initial_locks_empty(self):
        det = DeadlockDetector()
        assert det.locks == {}

    def test_initial_preemption_order_empty(self):
        det = DeadlockDetector()
        assert det.preemption_order == []


class TestAddEdge:
    def test_add_single_edge(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        assert "B" in det.wait_graph["A"]

    def test_add_multiple_edges_same_waiter(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        det.add_edge("A", "C")
        assert det.wait_graph["A"] == {"B", "C"}

    def test_add_duplicate_edge_no_duplication(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        det.add_edge("A", "B")
        assert det.wait_graph["A"] == {"B"}


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
        assert "A" not in det.wait_graph

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
        assert det.locks["res1"] == "holder1"

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
        assert "res1" not in det.locks

    def test_release_by_non_owner_fails(self):
        det = DeadlockDetector()
        det.try_acquire("res1", "holder1")
        result = det.release("res1", "holder2")
        assert result is False
        assert det.locks["res1"] == "holder1"

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
        assert len(det.preemption_order) > 0


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
        assert victim not in det.wait_graph

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


class TestDetectCycleFullPath:
    def test_returns_full_cycle_path(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        det.add_edge("B", "C")
        det.add_edge("C", "A")
        result = det.detect_cycle()
        assert len(result) == 3
        assert set(result) == {"A", "B", "C"}

    def test_two_node_cycle_returns_both(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        det.add_edge("B", "A")
        result = det.detect_cycle()
        assert len(result) == 2
        assert set(result) == {"A", "B"}

    def test_self_loop_returns_single_node(self):
        det = DeadlockDetector()
        det.add_edge("A", "A")
        result = det.detect_cycle()
        assert result == ["A"]

    def test_no_cycle_returns_empty_list(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        det.add_edge("B", "C")
        result = det.detect_cycle()
        assert result == []


class TestDetectCycleWithArgs:
    def test_detect_cycle_accepts_waiter_holder(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        det.add_edge("B", "A")
        result = det.detect_cycle("C", "A")
        assert len(result) > 0

    def test_detect_cycle_with_args_adds_edge(self):
        det = DeadlockDetector()
        result = det.detect_cycle("X", "Y")
        assert "Y" in det.wait_graph.get("X", set())

    def test_detect_cycle_with_none_args_ignores(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        result = det.detect_cycle(None, None)
        assert result == []


class TestBreakTimeout:
    def test_break_timeout_returns_expired_resources(self):
        det = DeadlockDetector()
        det.try_acquire("res1", "holder1")
        result = det.break_timeout(0.0)
        assert "res1" in result

    def test_break_timeout_removes_expired_locks(self):
        det = DeadlockDetector()
        det.try_acquire("res1", "holder1")
        det.break_timeout(0.0)
        assert "res1" not in det.locks

    def test_break_timeout_keeps_active_locks(self):
        det = DeadlockDetector()
        det.try_acquire("res1", "holder1")
        result = det.break_timeout(100.0)
        assert result == []
        assert "res1" in det.locks

    def test_break_timeout_clears_timestamps(self):
        det = DeadlockDetector()
        det.try_acquire("res1", "holder1")
        det.break_timeout(0.0)
        assert "res1" not in det.lock_timestamps

    def test_break_timeout_empty_returns_empty(self):
        det = DeadlockDetector()
        result = det.break_timeout(10.0)
        assert result == []


class TestDijkstraOrderFixed:
    def test_in_degree_calculated_correctly(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        det.add_edge("A", "C")
        det.add_edge("B", "C")
        order = det.dijkstra_order()
        assert order.index("A") < order.index("B")
        assert order.index("A") < order.index("C")
        assert order.index("B") < order.index("C")

    def test_diamond_dependency(self):
        det = DeadlockDetector()
        det.add_edge("A", "B")
        det.add_edge("A", "C")
        det.add_edge("B", "D")
        det.add_edge("C", "D")
        order = det.dijkstra_order()
        assert order.index("A") < order.index("B")
        assert order.index("A") < order.index("C")
        assert order.index("B") < order.index("D")
        assert order.index("C") < order.index("D")


class TestBreakDeadlockCleansLocks:
    def test_break_deadlock_removes_holder_locks(self):
        det = DeadlockDetector()
        det.try_acquire("res1", "holder1")
        det.break_deadlock("holder1")
        assert "res1" not in det.locks

    def test_break_deadlock_clears_timestamps(self):
        det = DeadlockDetector()
        det.try_acquire("res1", "holder1")
        det.break_deadlock("holder1")
        assert "res1" not in det.lock_timestamps


class TestReleaseCleansTimestamps:
    def test_release_clears_timestamp(self):
        det = DeadlockDetector()
        det.try_acquire("res1", "holder1")
        det.release("res1", "holder1")
        assert "res1" not in det.lock_timestamps


class TestDelegationEngineIntegration:
    def test_delegation_engine_uses_deadlock_detector(self, monkeypatch):
        from zephyr.governance.escalation.escalation_models import EscalationEvent, RuleCategory
        from zephyr.governance.intelligence_governance.delegation_engine import DelegationEngine
        from zephyr.governance.resilience_governance.deadlock_detector import DeadlockDetector

        det = DeadlockDetector()
        engine = DelegationEngine(deadlock_detector=det)
        monkeypatch.setattr(engine, "lsg_verify_delegation", lambda event: None)
        engine.register_delegate("delegate1", ["custom"])

        event = EscalationEvent(
            category=RuleCategory.CUSTOM,
            description="test",
            owner_id="owner1",
        )
        det.add_edge("owner1", "delegate1")
        det.add_edge("delegate1", "owner1")

        record = engine.delegate(event, task_id="task1")
        assert record.deadlock_detected is True

    def test_delegation_engine_no_deadlock_proceeds(self, monkeypatch):
        from zephyr.governance.escalation.escalation_models import EscalationEvent, RuleCategory
        from zephyr.governance.intelligence_governance.delegation_engine import DelegationEngine
        from zephyr.governance.resilience_governance.deadlock_detector import DeadlockDetector

        det = DeadlockDetector()
        engine = DelegationEngine(deadlock_detector=det)
        monkeypatch.setattr(engine, "lsg_verify_delegation", lambda event: None)
        engine.register_delegate("delegate1", ["custom"])

        event = EscalationEvent(
            category=RuleCategory.CUSTOM,
            description="test",
            owner_id="owner1",
        )
        record = engine.delegate(event, task_id="task2")
        assert record.deadlock_detected is False
        assert record.to_delegate == "delegate1"
