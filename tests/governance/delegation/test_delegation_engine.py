# [A_test] module_id: MOD-GOV_delegation_engine | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_delegation_engine
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] must test all public classes and methods of delegation_engine
# [MODIFY-GUARD] delegation_engine.py changes require sync
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/test_delegation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from unittest.mock import patch

import pytest

from zephyr.governance.escalation.escalation_models import (
    DelegationStrategy,
    EscalationEvent,
    EscalationLevel,
    RuleCategory,
)
from zephyr.governance.intelligence_governance.delegation_engine import DelegationEngine


def _make_event(owner_id="owner1", description="test event"):
    return EscalationEvent(
        owner_id=owner_id,
        description=description,
        category=RuleCategory.TIMEOUT,
        level=EscalationLevel.L2_HUMAN_REVIEW,
    )


@pytest.fixture(autouse=True)
def _mock_lsg():
    with patch.object(DelegationEngine, "lsg_verify_delegation"):
        yield


class TestDelegationEngine:
    def test_instantiation(self):
        engine = DelegationEngine()
        assert engine.MAX_LOAD_PER_DELEGATE == 5
        assert engine.DELEGATION_TIMEOUT_HOURS == 24

    def test_register_delegate(self):
        engine = DelegationEngine()
        engine.register_delegate("d1", expertise=["operational"])
        assert engine.get_load("d1") == 0

    def test_unregister_delegate(self):
        engine = DelegationEngine()
        engine.register_delegate("d1")
        engine.unregister_delegate("d1")
        assert engine.get_load("d1") == 0

    def test_delegate_load_balanced(self):
        engine = DelegationEngine()
        engine.register_delegate("d1")
        engine.register_delegate("d2")
        event = _make_event()
        record = engine.delegate(event, strategy=DelegationStrategy.LOAD_BALANCED)
        assert record.to_delegate in ("d1", "d2")
        assert engine.get_load(record.to_delegate) == 1

    def test_delegate_round_robin(self):
        engine = DelegationEngine()
        engine.register_delegate("d1")
        engine.register_delegate("d2")
        event1 = _make_event()
        event2 = _make_event()
        r1 = engine.delegate(event1, strategy=DelegationStrategy.ROUND_ROBIN)
        r2 = engine.delegate(event2, strategy=DelegationStrategy.ROUND_ROBIN)
        assert r1.to_delegate != r2.to_delegate

    def test_delegate_expertise_match(self):
        engine = DelegationEngine()
        engine.register_delegate("d1", expertise=["operational"])
        engine.register_delegate("d2", expertise=["security"])
        event = _make_event()
        record = engine.delegate(event, strategy=DelegationStrategy.EXPERTISE_MATCH)
        assert record.to_delegate == "d1"

    def test_delegate_no_available(self):
        engine = DelegationEngine()
        event = _make_event()
        record = engine.delegate(event)
        assert record.to_delegate == ""

    def test_delegate_self_delegation_prevented(self):
        engine = DelegationEngine()
        engine.register_delegate("owner1")
        event = _make_event(owner_id="owner1")
        record = engine.delegate(event)
        assert record.to_delegate == ""

    def test_accept_delegation(self):
        engine = DelegationEngine()
        engine.register_delegate("d1")
        event = _make_event()
        record = engine.delegate(event)
        result = engine.accept_delegation(record.delegation_id)
        assert result is True

    def test_accept_delegation_not_found(self):
        engine = DelegationEngine()
        result = engine.accept_delegation("nonexistent")
        assert result is False

    def test_complete_delegation(self):
        engine = DelegationEngine()
        engine.register_delegate("d1")
        event = _make_event()
        record = engine.delegate(event)
        result = engine.complete_delegation(record.delegation_id)
        assert result is True
        assert engine.get_load("d1") == 0

    def test_complete_delegation_not_found(self):
        engine = DelegationEngine()
        result = engine.complete_delegation("nonexistent")
        assert result is False

    def test_reject_delegation(self):
        engine = DelegationEngine()
        engine.register_delegate("d1")
        event = _make_event()
        record = engine.delegate(event)
        result = engine.reject_delegation(record.delegation_id)
        assert result is True
        assert engine.get_load("d1") == 0

    def test_get_available_delegates(self):
        engine = DelegationEngine()
        engine.register_delegate("d1")
        assert "d1" in engine.get_available_delegates()

    def test_get_available_delegates_overloaded(self):
        engine = DelegationEngine()
        engine.register_delegate("d1")
        for _ in range(5):
            engine.delegate_load["d1"] += 1
        assert "d1" not in engine.get_available_delegates()

    def test_get_pending_delegations(self):
        engine = DelegationEngine()
        engine.register_delegate("d1")
        event = _make_event()
        engine.delegate(event)
        pending = engine.get_pending_delegations()
        assert len(pending) == 1

    def test_cleanup_expired(self):
        engine = DelegationEngine()
        count = engine.cleanup_expired()
        assert count == 0


class TestDelegationDepth:
    def test_depth_limit_blocks_after_max(self):
        engine = DelegationEngine()
        engine.register_delegate("d1")
        for _ in range(DelegationEngine.MAX_DELEGATION_DEPTH):
            event = _make_event()
            engine.delegate(event, task_id="task-1")
        event = _make_event()
        record = engine.delegate(event, task_id="task-1")
        assert record.depth_exceeded is True
        assert record.to_delegate == ""

    def test_depth_tracks_per_task(self):
        engine = DelegationEngine()
        engine.register_delegate("d1")
        engine.register_delegate("d2")
        engine.delegate(_make_event(), task_id="task-A")
        engine.delegate(_make_event(), task_id="task-B")
        assert engine.get_delegation_depth("task-A") == 1
        assert engine.get_delegation_depth("task-B") == 1

    def test_get_delegation_depth_returns_zero_for_unknown(self):
        engine = DelegationEngine()
        assert engine.get_delegation_depth("unknown") == 0


class TestDelegationHistory:
    def test_history_records_delegations(self):
        engine = DelegationEngine()
        engine.register_delegate("d1")
        engine.delegate(_make_event())
        history = engine.get_delegation_history()
        assert len(history) == 1

    def test_get_delegation_history_returns_copy(self):
        engine = DelegationEngine()
        engine.register_delegate("d1")
        engine.delegate(_make_event())
        h1 = engine.get_delegation_history()
        h2 = engine.get_delegation_history()
        assert h1 is not h2
        assert h1 == h2


class TestDeadlockDetectorIntegration:
    def test_deadlock_detected_blocks_delegation(self):
        class MockDeadlockDetector:
            def detect_cycle(self, owner_id, target_id):
                return ["owner1", "d1", "owner1"]

        engine = DelegationEngine(deadlock_detector=MockDeadlockDetector())
        engine.register_delegate("d1")
        event = _make_event(owner_id="owner1")
        record = engine.delegate(event)
        assert record.deadlock_detected is True
        assert record.to_delegate == ""

    def test_no_deadlock_allows_delegation(self):
        class MockDeadlockDetector:
            def detect_cycle(self, owner_id, target_id):
                return None

        engine = DelegationEngine(deadlock_detector=MockDeadlockDetector())
        engine.register_delegate("d1")
        event = _make_event(owner_id="owner1")
        record = engine.delegate(event)
        assert record.deadlock_detected is False
        assert record.to_delegate == "d1"

    def test_deadlock_detector_exception_does_not_block(self):
        class FailingDeadlockDetector:
            def detect_cycle(self, owner_id, target_id):
                raise RuntimeError("detector error")

        engine = DelegationEngine(deadlock_detector=FailingDeadlockDetector())
        engine.register_delegate("d1")
        event = _make_event(owner_id="owner1")
        record = engine.delegate(event)
        assert record.deadlock_detected is False
        assert record.to_delegate == "d1"
