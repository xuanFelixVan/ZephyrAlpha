# [A_test] module_id: MOD-GOV_f5_red_team_extreme | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §4
# [MODULE] tests.test_f5_red_team_extreme
# [INVARIANTS] Tests must not modify production state; All imports guarded by pytest.importorskip; Concurrency via ThreadPoolExecutor only
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError → skip; AttributeError → fail
# [TESTS] python -m pytest tests/test_f5_red_team_extreme.py -v --timeout=60
# [TTL] task_bound

"""F5 红蓝对抗极端测试 — DM-201513

5类极端场景压测:
  1. 管线全堵塞→DLQ溢出: DeadlockDetector检测+break_deadlock
  2. 背压级联崩溃: CascadeGuard防护
  3. SLO预算耗尽: EscalationEngine降级
  4. FeedbackLoop异常: DeadlockDetector.detect_cycle检测
  5. 并发100任务混合场景: 整体稳定性
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch

import pytest

dd_mod = pytest.importorskip(
    "zephyr.governance.resilience_governance.deadlock_detector",
    reason="deadlock_detector module not available",
)
delegation_mod = pytest.importorskip(
    "zephyr.governance.intelligence_governance.delegation_engine",
    reason="delegation_engine module not available",
)
escalation_api_mod = pytest.importorskip(
    "zephyr.governance.escalation.escalation_api",
    reason="escalation_api module not available",
)
escalation_engine_mod = pytest.importorskip(
    "zephyr.governance.escalation.escalation_engine",
    reason="escalation_engine module not available",
)
cascade_mod = pytest.importorskip(
    "zephyr.infrastructure.a2a_protocol.layer3_coordination.cascade_guard",
    reason="cascade_guard module not available",
)
loop_mod = pytest.importorskip(
    "zephyr.governance.escalation.escalation_loop_detector",
    reason="escalation_loop_detector module not available",
)
arbitrator_mod = pytest.importorskip(
    "zephyr.infrastructure.a2a_protocol.layer3_coordination.arbitrator",
    reason="arbitrator module not available",
)

from zephyr.governance.escalation.escalation_api import EscalationAPI
from zephyr.governance.escalation.escalation_engine import EscalationEngine
from zephyr.governance.escalation.escalation_loop_detector import EscalationLoopDetector
from zephyr.governance.escalation.escalation_models import (
    DelegationStrategy,
    EscalationEvent,
    EscalationLevel,
    EscalationState,
    RuleCategory,
)
from zephyr.governance.intelligence_governance.delegation_engine import DelegationEngine
from zephyr.governance.resilience_governance.deadlock_detector import DeadlockDetector
from zephyr.infrastructure.a2a_protocol.layer3_coordination.arbitrator import (
    AgentMeta,
    AgentRole,
    ArbitrationVerdict,
    Arbitrator,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.cascade_guard import (
    CascadeGuard,
)


def _make_event(
    owner_id: str = "owner1",
    description: str = "test event",
    category: RuleCategory = RuleCategory.TIMEOUT,
    level: EscalationLevel = EscalationLevel.L2_HUMAN_REVIEW,
) -> EscalationEvent:
    return EscalationEvent(
        owner_id=owner_id,
        description=description,
        category=category,
        level=level,
    )


@pytest.fixture(autouse=True)
def _mock_lsg():
    with patch.object(DelegationEngine, "lsg_verify_delegation"), patch.object(EscalationEngine, "lsg_scan_input"):
        yield


class TestPipelineFullBlockageDLQOverflow:
    """场景1: 管线全堵塞→DLQ溢出 — 验证DeadlockDetector检测+break_deadlock。"""

    def test_all_agents_blocked_cycle_detected(self):
        det = DeadlockDetector()
        agents = [f"agent_{i}" for i in range(10)]
        for i in range(len(agents)):
            det.add_edge(agents[i], agents[(i + 1) % len(agents)])
        cycle = det.detect_cycle()
        assert len(cycle) > 0, "全堵塞场景必须检测到循环"

    def test_dlq_overflow_break_deadlock_resolves_cycle(self):
        det = DeadlockDetector()
        for i in range(20):
            det.add_edge(f"waiter_{i}", f"holder_{i}")
            det.add_edge(f"holder_{i}", f"waiter_{(i + 1) % 20}")
        cycle = det.detect_cycle()
        assert len(cycle) > 0
        victim = cycle[0]
        result = det.break_deadlock(victim)
        assert result is True
        assert victim not in det.wait_graph

    def test_concurrent_edge_addition_threadsafe(self):
        det = DeadlockDetector()

        def add_edges_batch(start: int) -> int:
            for i in range(start, start + 50):
                det.add_edge(f"w_{i}", f"h_{i}")
            return 50

        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(add_edges_batch, i * 50) for i in range(8)]
            total = sum(f.result() for f in as_completed(futures))
        assert total == 400
        assert len(det.wait_graph) == 400

    def test_break_all_blocked_agents_clears_graph(self):
        det = DeadlockDetector()
        agents = [f"a_{i}" for i in range(15)]
        for i in range(len(agents)):
            det.add_edge(agents[i], agents[(i + 1) % len(agents)])
        for agent in agents:
            det.break_deadlock(agent)
        assert det.wait_graph == {}

    def test_break_timeout_clears_expired_locks_under_load(self):
        det = DeadlockDetector()
        for i in range(50):
            det.try_acquire(f"res_{i}", f"holder_{i}")
        expired = det.break_timeout(0.0)
        assert len(expired) == 50
        assert det.locks == {}


class TestBackpressureCascadeCollapse:
    """场景2: 背压级联崩溃 — 验证CascadeGuard防护。"""

    def test_cascade_guard_blocks_after_threshold(self):
        guard = CascadeGuard(threshold=5)
        for _ in range(5):
            guard.record_failure("agent_a")
        assert guard.check("agent_a") is False

    def test_cascade_guard_allows_below_threshold(self):
        guard = CascadeGuard(threshold=10)
        for _ in range(9):
            guard.record_failure("agent_b")
        assert guard.check("agent_b") is True

    def test_concurrent_cascade_failures_isolated(self):
        guard = CascadeGuard(threshold=10)
        agent_ids = [f"agent_{i}" for i in range(20)]

        def record_failures(agent_id: str) -> int:
            count = 0
            for _ in range(15):
                count = guard.record_failure(agent_id)
            return count

        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(record_failures, aid) for aid in agent_ids]
            counts = [f.result() for f in as_completed(futures)]
        assert all(c == 15 for c in counts)
        blocked = [aid for aid in agent_ids if not guard.check(aid)]
        assert len(blocked) == 20

    def test_cascade_failure_escalation_handled(self):
        engine = EscalationEngine(hooks_enabled=False)
        event = engine.evaluate(
            category=RuleCategory.CASCADE_FAILURE,
            description="cascade failure simulation",
            owner_id="agent_cascade",
        )
        assert event.category == RuleCategory.CASCADE_FAILURE
        assert event.state in (EscalationState.EVALUATING, EscalationState.REJECTED)

    def test_cascade_guard_per_agent_isolation(self):
        guard = CascadeGuard(threshold=3)
        guard.record_failure("agent_x")
        guard.record_failure("agent_x")
        assert guard.check("agent_y") is True
        assert guard.check("agent_x") is True
        guard.record_failure("agent_x")
        assert guard.check("agent_x") is False
        assert guard.check("agent_y") is True


class TestSLOBudgetExhaustion:
    """场景3: SLO预算耗尽 — 验证EscalationEngine降级。"""

    def test_economic_guard_blocks_after_budget_exhausted(self):
        engine = EscalationEngine(hooks_enabled=False)
        engine.economic_guard.daily_budget = 5.0
        engine.economic_guard.consumed_today = 5.0
        engine.economic_guard.hard_limit_reached = True
        event = engine.evaluate(
            category=RuleCategory.DEADLOCK,
            description="budget exhausted test",
            owner_id="owner_budget",
        )
        assert event.economic_guard_passed is False
        assert event.state == EscalationState.REJECTED

    def test_escalation_api_rate_limit_enforced(self):
        api = EscalationAPI(engine=None, rate_limit_per_hour=3)
        api.register_service("svc", "key-1")
        results = []
        for _ in range(5):
            r = api.trigger_escalation("svc", "key-1", "op")
            results.append(r["status"])
        assert results.count("escalated") == 3
        assert results.count("rate_limited") == 2

    def test_concurrent_budget_consumption_threadsafe(self):
        engine = EscalationEngine(hooks_enabled=False)
        engine.economic_guard.daily_budget = 1000.0

        def evaluate_one(idx: int) -> str:
            event = engine.evaluate(
                category=RuleCategory.CUSTOM,
                description=f"concurrent budget test {idx}",
                owner_id=f"owner_{idx}",
            )
            return event.state.name

        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(evaluate_one, i) for i in range(50)]
            states = [f.result() for f in as_completed(futures)]
        assert len(states) == 50
        assert all(s in ("EVALUATING", "REJECTED") for s in states)

    def test_budget_exhausted_category_rejected(self):
        engine = EscalationEngine(hooks_enabled=False)
        engine.economic_guard.daily_budget = 0.0
        engine.economic_guard.hard_limit_reached = True
        event = engine.evaluate(
            category=RuleCategory.BUDGET_EXCEEDED,
            description="budget zero",
            owner_id="owner_zero",
        )
        assert event.state == EscalationState.REJECTED

    def test_api_audit_log_records_rate_limited(self):
        api = EscalationAPI(engine=None, rate_limit_per_hour=2)
        api.register_service("svc", "key-1")
        for _ in range(4):
            api.trigger_escalation("svc", "key-1", "op")
        log = api.get_audit_log()
        rate_limited_entries = [e for e in log if e["status"] == "rate_limited"]
        assert len(rate_limited_entries) == 2


class TestFeedbackLoopAnomaly:
    """场景4: FeedbackLoop异常 — 验证DeadlockDetector.detect_cycle检测。"""

    def test_feedback_loop_cycle_detected(self):
        det = DeadlockDetector()
        det.add_edge("feedback_a", "feedback_b")
        det.add_edge("feedback_b", "feedback_c")
        det.add_edge("feedback_c", "feedback_a")
        cycle = det.detect_cycle()
        assert len(cycle) == 3
        assert set(cycle) == {"feedback_a", "feedback_b", "feedback_c"}

    def test_escalation_loop_detector_catches_loop(self):
        detector = EscalationLoopDetector()
        for _ in range(4):
            detector.record_transition("task_loop", "L0", "L1")
            detector.record_transition("task_loop", "L1", "L0")
        assert detector.detect_loop(window_s=300) is True

    def test_concurrent_loop_detection_stable(self):
        det = DeadlockDetector()

        def build_loop(idx: int) -> bool:
            nodes = [f"n_{idx}_{i}" for i in range(5)]
            for i in range(5):
                det.add_edge(nodes[i], nodes[(i + 1) % 5])
            cycle = det.detect_cycle()
            return len(cycle) > 0

        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(build_loop, i) for i in range(20)]
            results = [f.result() for f in as_completed(futures)]
        assert all(results)

    def test_self_loop_detected_as_anomaly(self):
        det = DeadlockDetector()
        det.add_edge("self_loop_agent", "self_loop_agent")
        cycle = det.detect_cycle()
        assert len(cycle) > 0
        assert "self_loop_agent" in cycle

    def test_break_deadlock_resolves_feedback_loop(self):
        det = DeadlockDetector()
        det.add_edge("fb_a", "fb_b")
        det.add_edge("fb_b", "fb_c")
        det.add_edge("fb_c", "fb_a")
        cycle = det.detect_cycle()
        assert len(cycle) > 0
        det.break_deadlock(cycle[0])
        after = det.detect_cycle()
        assert after == []


class TestConcurrent100TasksMixed:
    """场景5: 并发100任务混合场景 — 验证整体稳定性。"""

    def test_100_concurrent_delegations_stable(self):
        det = DeadlockDetector()
        engine = DelegationEngine(deadlock_detector=det)
        for i in range(10):
            engine.register_delegate(f"delegate_{i}", expertise=["custom"])

        def delegate_one(idx: int) -> str:
            event = _make_event(
                owner_id=f"owner_{idx}",
                description=f"concurrent task {idx}",
                category=RuleCategory.CUSTOM,
            )
            record = engine.delegate(event, task_id=f"task_{idx}")
            return record.to_delegate

        with ThreadPoolExecutor(max_workers=16) as pool:
            futures = [pool.submit(delegate_one, i) for i in range(100)]
            results = [f.result() for f in as_completed(futures)]
        assert len(results) == 100
        assert all(isinstance(r, str) for r in results)

    def test_100_concurrent_escalations_stable(self):
        engine = EscalationEngine(hooks_enabled=False)
        engine.economic_guard.daily_budget = 10000.0

        def evaluate_one(idx: int) -> str:
            event = engine.evaluate(
                category=RuleCategory.CUSTOM,
                description=f"mixed escalation {idx}",
                owner_id=f"owner_{idx}",
            )
            return event.state.name

        with ThreadPoolExecutor(max_workers=16) as pool:
            futures = [pool.submit(evaluate_one, i) for i in range(100)]
            states = [f.result() for f in as_completed(futures)]
        assert len(states) == 100
        assert all(s in ("EVALUATING", "REJECTED") for s in states)

    def test_100_concurrent_deadlock_checks_stable(self):
        det = DeadlockDetector()

        def add_and_detect(idx: int) -> bool:
            det.add_edge(f"mix_w_{idx}", f"mix_h_{idx}")
            if idx % 10 == 0:
                det.add_edge(f"mix_h_{idx}", f"mix_w_{idx - 10}")
            cycle = det.detect_cycle()
            return isinstance(cycle, list)

        with ThreadPoolExecutor(max_workers=16) as pool:
            futures = [pool.submit(add_and_detect, i) for i in range(100)]
            results = [f.result() for f in as_completed(futures)]
        assert len(results) == 100
        assert all(results)

    def test_100_concurrent_arbitrations_stable(self):
        det = DeadlockDetector()
        arb = Arbitrator(deadlock_detector=det)
        roles = [AgentRole.BUILDER, AgentRole.REVIEWER, AgentRole.GOVERNANCE]

        def arbitrate_one(idx: int) -> int:
            a = AgentMeta(
                agent_id=f"agent_a_{idx}",
                role=roles[idx % 3],
                tasks_completed=idx,
            )
            b = AgentMeta(
                agent_id=f"agent_b_{idx}",
                role=roles[(idx + 1) % 3],
                tasks_completed=idx + 1,
            )
            result = arb.arbitrate(a, b, [f"file_{idx}.py"])
            return result.tier

        with ThreadPoolExecutor(max_workers=16) as pool:
            futures = [pool.submit(arbitrate_one, i) for i in range(100)]
            tiers = [f.result() for f in as_completed(futures)]
        assert len(tiers) == 100
        assert all(t in (1, 2, 3) for t in tiers)

    def test_100_mixed_all_components_stable(self):
        det = DeadlockDetector()
        engine = DelegationEngine(deadlock_detector=det)
        esc_engine = EscalationEngine(hooks_enabled=False)
        esc_engine.economic_guard.daily_budget = 10000.0
        arb = Arbitrator(deadlock_detector=det)
        guard = CascadeGuard(threshold=1000)
        for i in range(10):
            engine.register_delegate(f"mix_del_{i}")

        def mixed_task(idx: int) -> str:
            op_type = idx % 4
            if op_type == 0:
                event = _make_event(
                    owner_id=f"mix_owner_{idx}",
                    description=f"mixed delegate {idx}",
                    category=RuleCategory.CUSTOM,
                )
                record = engine.delegate(event, task_id=f"mix_task_{idx}")
                return f"delegate:{record.to_delegate}"
            elif op_type == 1:
                event = esc_engine.evaluate(
                    category=RuleCategory.CUSTOM,
                    description=f"mixed esc {idx}",
                    owner_id=f"mix_owner_{idx}",
                )
                return f"escalation:{event.state.name}"
            elif op_type == 2:
                a = AgentMeta(agent_id=f"mix_a_{idx}", role=AgentRole.BUILDER)
                b = AgentMeta(agent_id=f"mix_b_{idx}", role=AgentRole.REVIEWER)
                result = arb.arbitrate(a, b, [f"mix_file_{idx}.py"])
                return f"arbitration:{result.tier}"
            else:
                det.add_edge(f"mix_w_{idx}", f"mix_h_{idx}")
                guard.record_failure(f"mix_agent_{idx}")
                return "deadlock+guard:ok"

        with ThreadPoolExecutor(max_workers=16) as pool:
            futures = [pool.submit(mixed_task, i) for i in range(100)]
            results = [f.result() for f in as_completed(futures)]
        assert len(results) == 100
        assert all(isinstance(r, str) and r for r in results)
