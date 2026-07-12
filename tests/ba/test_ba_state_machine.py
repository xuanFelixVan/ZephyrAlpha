# [A_test] module_id: SRC-TST-0403 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_ba_state_machine
# [INVARIANTS] 状态转换必须合法
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from zephyr.gov_drift.drift_models import DriftState
from zephyr.infrastructure.auto_fix_engine.state_machine import (
    TERMINAL_STATES,
    DriftEventRecord,
    DriftStateMachine,
    InvalidTransitionError,
)


class TestDriftEventRecord:
    def test_instantiation_with_defaults(self):
        eid = uuid.uuid4()
        rec = DriftEventRecord(event_id=eid, state=DriftState.DETECTED)
        assert rec.event_id == eid
        assert rec.state == DriftState.DETECTED
        assert rec.resolved_by is None
        assert rec.auto_fixable is False
        assert rec.needs_human is False
        assert rec.suppressed_until is None

    def test_instantiation_with_times(self):
        now = datetime.now(UTC)
        eid = uuid.uuid4()
        rec = DriftEventRecord(
            event_id=eid,
            state=DriftState.TRIAGED,
            created_at=now,
            updated_at=now,
        )
        assert rec.created_at == now
        assert rec.updated_at == now


class TestDriftStateMachineInit:
    def test_initial_state(self):
        sm = DriftStateMachine()
        assert sm.TTL_DETECTED_HOURS == 24
        assert len(sm._events) == 0


class TestValidateTransition:
    def test_valid_detected_to_triaged(self):
        sm = DriftStateMachine()
        assert sm.validate_transition(DriftState.DETECTED, DriftState.TRIAGED) is True

    def test_valid_detected_to_acknowledged(self):
        sm = DriftStateMachine()
        assert sm.validate_transition(DriftState.DETECTED, DriftState.ACKNOWLEDGED) is True

    def test_valid_detected_to_false_positive(self):
        sm = DriftStateMachine()
        assert sm.validate_transition(DriftState.DETECTED, DriftState.FALSE_POSITIVE) is True

    def test_valid_detected_to_dead_letter(self):
        sm = DriftStateMachine()
        assert sm.validate_transition(DriftState.DETECTED, DriftState.DEAD_LETTER) is True

    def test_invalid_detected_to_resolved(self):
        sm = DriftStateMachine()
        assert sm.validate_transition(DriftState.DETECTED, DriftState.RESOLVED) is False

    def test_invalid_verified_to_anything(self):
        sm = DriftStateMachine()
        assert sm.validate_transition(DriftState.VERIFIED, DriftState.DETECTED) is False

    def test_invalid_false_positive_to_anything(self):
        sm = DriftStateMachine()
        assert sm.validate_transition(DriftState.FALSE_POSITIVE, DriftState.DETECTED) is False

    def test_fix_failed_to_acknowledged(self):
        sm = DriftStateMachine()
        assert sm.validate_transition(DriftState.FIX_FAILED, DriftState.ACKNOWLEDGED) is True

    def test_resolving_to_fix_failed(self):
        sm = DriftStateMachine()
        assert sm.validate_transition(DriftState.RESOLVING, DriftState.FIX_FAILED) is True

    def test_resolving_to_resolved(self):
        sm = DriftStateMachine()
        assert sm.validate_transition(DriftState.RESOLVING, DriftState.RESOLVED) is True

    def test_suppressed_to_detected(self):
        sm = DriftStateMachine()
        assert sm.validate_transition(DriftState.SUPPRESSED, DriftState.DETECTED) is True


class TestTransition:
    def test_successful_transition(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        result = sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        assert result == DriftState.TRIAGED

    def test_invalid_transition_raises(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        with pytest.raises(InvalidTransitionError):
            sm.transition(eid, DriftState.DETECTED, DriftState.RESOLVED)

    def test_state_mismatch_raises(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        with pytest.raises(InvalidTransitionError):
            sm.transition(eid, DriftState.DETECTED, DriftState.ACKNOWLEDGED)

    def test_resolved_by_recorded(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(eid, DriftState.TRIAGED, DriftState.ACKNOWLEDGED)
        sm.transition(eid, DriftState.ACKNOWLEDGED, DriftState.RESOLVING)
        sm.transition(
            eid,
            DriftState.RESOLVING,
            DriftState.RESOLVED,
            resolved_by="agent-1",
        )
        rec = sm._events[eid]
        assert rec.resolved_by == "agent-1"
        assert rec.resolved_at is not None

    def test_resolution_detail_recorded(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(
            eid,
            DriftState.TRIAGED,
            DriftState.ACKNOWLEDGED,
            resolution_detail="manual review",
        )
        rec = sm._events[eid]
        assert rec.resolution_detail == "manual review"


class TestAutoTransition:
    def test_triaged_auto_fixable_transitions_to_resolving(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        sm.mark_auto_fixable(eid)
        result = sm.auto_transition(eid)
        assert result == DriftState.RESOLVING

    def test_triaged_not_auto_fixable_returns_none(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        result = sm.auto_transition(eid)
        assert result is None

    def test_fix_failed_transitions_to_acknowledged(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(eid, DriftState.TRIAGED, DriftState.ACKNOWLEDGED)
        sm.transition(eid, DriftState.ACKNOWLEDGED, DriftState.RESOLVING)
        sm.transition(eid, DriftState.RESOLVING, DriftState.FIX_FAILED)
        result = sm.auto_transition(eid)
        assert result == DriftState.ACKNOWLEDGED

    def test_resolved_transitions_to_verified(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(eid, DriftState.TRIAGED, DriftState.ACKNOWLEDGED)
        sm.transition(eid, DriftState.ACKNOWLEDGED, DriftState.RESOLVING)
        sm.transition(eid, DriftState.RESOLVING, DriftState.RESOLVED)
        result = sm.auto_transition(eid)
        assert result == DriftState.VERIFIED

    def test_unknown_event_returns_none(self):
        sm = DriftStateMachine()
        result = sm.auto_transition(uuid.uuid4())
        assert result is None


class TestCheckTtl:
    def test_expired_detected_moves_to_dead_letter(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(eid, DriftState.TRIAGED, DriftState.ACKNOWLEDGED)
        sm.transition(eid, DriftState.ACKNOWLEDGED, DriftState.RESOLVING)
        sm.transition(eid, DriftState.RESOLVING, DriftState.FIX_FAILED)
        sm.transition(eid, DriftState.FIX_FAILED, DriftState.ACKNOWLEDGED)
        sm.transition(eid, DriftState.ACKNOWLEDGED, DriftState.RESOLVING)
        sm.transition(eid, DriftState.RESOLVING, DriftState.FIX_FAILED)
        sm.transition(eid, DriftState.FIX_FAILED, DriftState.ACKNOWLEDGED)
        sm.transition(eid, DriftState.ACKNOWLEDGED, DriftState.RESOLVING)
        sm.transition(eid, DriftState.RESOLVING, DriftState.RESOLVED)
        sm.transition(eid, DriftState.RESOLVED, DriftState.VERIFIED)
        eid2 = uuid.uuid4()
        sm.transition(eid2, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(eid2, DriftState.TRIAGED, DriftState.ACKNOWLEDGED)
        sm.transition(eid2, DriftState.ACKNOWLEDGED, DriftState.RESOLVING)
        sm.transition(eid2, DriftState.RESOLVING, DriftState.RESOLVED)
        sm.transition(eid2, DriftState.RESOLVED, DriftState.VERIFIED)
        eid3 = uuid.uuid4()
        rec = DriftEventRecord(
            event_id=eid3,
            state=DriftState.DETECTED,
            created_at=datetime.now(UTC) - timedelta(hours=48),
        )
        sm._events[eid3] = rec
        expired = sm.check_ttl()
        assert eid3 in expired
        assert sm.get_state(eid3) == DriftState.DEAD_LETTER

    def test_fresh_detected_not_expired(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        expired = sm.check_ttl()
        assert eid not in expired

    def test_suppressed_expired_returns_to_detected(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(eid, DriftState.TRIAGED, DriftState.ACKNOWLEDGED)
        sm.transition(eid, DriftState.ACKNOWLEDGED, DriftState.RESOLVING)
        sm.transition(eid, DriftState.RESOLVING, DriftState.RESOLVED)
        sm.transition(eid, DriftState.RESOLVED, DriftState.VERIFIED)
        eid2 = uuid.uuid4()
        sm.transition(eid2, DriftState.DETECTED, DriftState.FALSE_POSITIVE)
        eid3 = uuid.uuid4()
        sm.transition(eid3, DriftState.DETECTED, DriftState.DEAD_LETTER)
        sm.transition(eid3, DriftState.DEAD_LETTER, DriftState.ACKNOWLEDGED)
        sm.transition(eid3, DriftState.ACKNOWLEDGED, DriftState.RESOLVING)
        sm.transition(eid3, DriftState.RESOLVING, DriftState.RESOLVED)
        sm.transition(eid3, DriftState.RESOLVED, DriftState.VERIFIED)
        eid4 = uuid.uuid4()
        sm.transition(eid4, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(eid4, DriftState.TRIAGED, DriftState.ACKNOWLEDGED)
        sm.transition(eid4, DriftState.ACKNOWLEDGED, DriftState.RESOLVING)
        sm.transition(eid4, DriftState.RESOLVING, DriftState.RESOLVED)
        sm.transition(eid4, DriftState.RESOLVED, DriftState.VERIFIED)
        eid_s = uuid.uuid4()
        sm.transition(eid_s, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(eid_s, DriftState.TRIAGED, DriftState.ACKNOWLEDGED)
        sm.transition(eid_s, DriftState.ACKNOWLEDGED, DriftState.RESOLVING)
        sm.transition(eid_s, DriftState.RESOLVING, DriftState.RESOLVED)
        sm.transition(eid_s, DriftState.RESOLVED, DriftState.VERIFIED)
        eid_s2 = uuid.uuid4()
        sm.transition(eid_s2, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(eid_s2, DriftState.TRIAGED, DriftState.ACKNOWLEDGED)
        sm.transition(eid_s2, DriftState.ACKNOWLEDGED, DriftState.RESOLVING)
        sm.transition(eid_s2, DriftState.RESOLVING, DriftState.RESOLVED)
        sm.transition(eid_s2, DriftState.RESOLVED, DriftState.VERIFIED)
        eid5 = uuid.uuid4()
        sm.transition(eid5, DriftState.DETECTED, DriftState.FALSE_POSITIVE)
        eid6 = uuid.uuid4()
        sm.transition(eid6, DriftState.DETECTED, DriftState.DEAD_LETTER)
        sm.transition(eid6, DriftState.DEAD_LETTER, DriftState.ACKNOWLEDGED)
        sm.transition(eid6, DriftState.ACKNOWLEDGED, DriftState.RESOLVING)
        sm.transition(eid6, DriftState.RESOLVING, DriftState.RESOLVED)
        sm.transition(eid6, DriftState.RESOLVED, DriftState.VERIFIED)
        eid7 = uuid.uuid4()
        rec7 = DriftEventRecord(event_id=eid7, state=DriftState.SUPPRESSED)
        rec7.suppressed_until = datetime.now(UTC) - timedelta(hours=1)
        sm._events[eid7] = rec7
        expired = sm.check_ttl()
        assert eid7 in expired
        assert sm.get_state(eid7) == DriftState.DETECTED


class TestSuppress:
    def test_suppress_raises_for_invalid_transition(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        expires = datetime.now(UTC) + timedelta(days=7)
        with pytest.raises(InvalidTransitionError):
            sm.suppress(eid, expires)

    def test_suppress_unknown_event_raises(self):
        sm = DriftStateMachine()
        with pytest.raises(InvalidTransitionError):
            sm.suppress(uuid.uuid4(), datetime.now(UTC) + timedelta(days=1))


class TestGetState:
    def test_returns_state_for_known_event(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        assert sm.get_state(eid) == DriftState.TRIAGED

    def test_returns_none_for_unknown_event(self):
        sm = DriftStateMachine()
        assert sm.get_state(uuid.uuid4()) is None


class TestIsTerminal:
    def test_verified_is_terminal(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(eid, DriftState.TRIAGED, DriftState.ACKNOWLEDGED)
        sm.transition(eid, DriftState.ACKNOWLEDGED, DriftState.RESOLVING)
        sm.transition(eid, DriftState.RESOLVING, DriftState.RESOLVED)
        sm.transition(eid, DriftState.RESOLVED, DriftState.VERIFIED)
        assert sm.is_terminal(eid) is True

    def test_false_positive_is_terminal(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.FALSE_POSITIVE)
        assert sm.is_terminal(eid) is True

    def test_detected_is_not_terminal(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        assert sm.is_terminal(eid) is False

    def test_unknown_event_is_not_terminal(self):
        sm = DriftStateMachine()
        assert sm.is_terminal(uuid.uuid4()) is False


class TestTerminalStates:
    def test_terminal_states_set(self):
        assert DriftState.VERIFIED in TERMINAL_STATES
        assert DriftState.FALSE_POSITIVE in TERMINAL_STATES
        assert DriftState.DETECTED not in TERMINAL_STATES
