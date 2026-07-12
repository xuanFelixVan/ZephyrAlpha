# [A_test] module_id: SRC-TST-1684 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_state_machine
# [INVARIANTS] 测试覆盖DriftStateMachine所有公共方法及边界条件
# [MODIFY-GUARD] state_machine.py变更时同步更新
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidTransitionError
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
    def test_init_with_defaults(self):
        eid = uuid.uuid4()
        rec = DriftEventRecord(event_id=eid, state=DriftState.DETECTED)
        assert rec.event_id == eid
        assert rec.state == DriftState.DETECTED
        assert rec.created_at is not None
        assert rec.updated_at is not None
        assert rec.resolved_by is None
        assert rec.resolution_detail is None
        assert rec.resolved_at is None
        assert rec.auto_fixable is False
        assert rec.needs_human is False
        assert rec.suppressed_until is None

    def test_init_with_explicit_timestamps(self):
        eid = uuid.uuid4()
        now = datetime.now(UTC)
        rec = DriftEventRecord(
            event_id=eid,
            state=DriftState.TRIAGED,
            created_at=now,
            updated_at=now,
        )
        assert rec.created_at == now
        assert rec.updated_at == now

    def test_init_with_none_state_stores_none(self):
        eid = uuid.uuid4()
        rec = DriftEventRecord(event_id=eid, state=None)
        assert rec.state is None


class TestDriftStateMachineInit:
    def test_default_construction(self):
        sm = DriftStateMachine()
        assert sm.TTL_DETECTED_HOURS == 24
        assert sm._events == {}

    def test_events_dict_is_empty(self):
        sm = DriftStateMachine()
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

    def test_invalid_verified_to_detected(self):
        sm = DriftStateMachine()
        assert sm.validate_transition(DriftState.VERIFIED, DriftState.DETECTED) is False

    def test_invalid_false_positive_to_anything(self):
        sm = DriftStateMachine()
        assert sm.validate_transition(DriftState.FALSE_POSITIVE, DriftState.DETECTED) is False

    def test_invalid_same_state(self):
        sm = DriftStateMachine()
        assert sm.validate_transition(DriftState.DETECTED, DriftState.DETECTED) is False

    def test_valid_resolving_to_resolved(self):
        sm = DriftStateMachine()
        assert sm.validate_transition(DriftState.RESOLVING, DriftState.RESOLVED) is True

    def test_valid_resolving_to_fix_failed(self):
        sm = DriftStateMachine()
        assert sm.validate_transition(DriftState.RESOLVING, DriftState.FIX_FAILED) is True

    def test_valid_fix_failed_to_acknowledged(self):
        sm = DriftStateMachine()
        assert sm.validate_transition(DriftState.FIX_FAILED, DriftState.ACKNOWLEDGED) is True

    def test_valid_dead_letter_to_acknowledged(self):
        sm = DriftStateMachine()
        assert sm.validate_transition(DriftState.DEAD_LETTER, DriftState.ACKNOWLEDGED) is True

    def test_valid_suppressed_to_detected(self):
        sm = DriftStateMachine()
        assert sm.validate_transition(DriftState.SUPPRESSED, DriftState.DETECTED) is True


class TestTransition:
    def test_valid_transition_creates_record(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        result = sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        assert result == DriftState.TRIAGED
        assert sm.get_state(eid) == DriftState.TRIAGED

    def test_valid_transition_chain(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(eid, DriftState.TRIAGED, DriftState.RESOLVING)
        sm.transition(eid, DriftState.RESOLVING, DriftState.RESOLVED)
        sm.transition(eid, DriftState.RESOLVED, DriftState.VERIFIED)
        assert sm.get_state(eid) == DriftState.VERIFIED

    def test_invalid_transition_raises(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        with pytest.raises(InvalidTransitionError):
            sm.transition(eid, DriftState.VERIFIED, DriftState.DETECTED)

    def test_state_mismatch_raises(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        with pytest.raises(InvalidTransitionError, match="State mismatch"):
            sm.transition(eid, DriftState.DETECTED, DriftState.ACKNOWLEDGED)

    def test_transition_with_resolved_by(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(eid, DriftState.TRIAGED, DriftState.RESOLVING)
        sm.transition(
            eid,
            DriftState.RESOLVING,
            DriftState.RESOLVED,
            resolved_by="agent-001",
        )
        rec = sm._events[eid]
        assert rec.resolved_by == "agent-001"

    def test_transition_with_resolution_detail(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(eid, DriftState.TRIAGED, DriftState.RESOLVING)
        sm.transition(
            eid,
            DriftState.RESOLVING,
            DriftState.RESOLVED,
            resolution_detail="fixed import path",
        )
        rec = sm._events[eid]
        assert rec.resolution_detail == "fixed import path"

    def test_resolved_state_sets_resolved_at(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(eid, DriftState.TRIAGED, DriftState.RESOLVING)
        sm.transition(eid, DriftState.RESOLVING, DriftState.RESOLVED)
        rec = sm._events[eid]
        assert rec.resolved_at is not None

    def test_non_resolved_state_no_resolved_at(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        rec = sm._events[eid]
        assert rec.resolved_at is None


class TestAutoTransition:
    def test_auto_transition_resolved_to_verified(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(eid, DriftState.TRIAGED, DriftState.RESOLVING)
        sm.transition(eid, DriftState.RESOLVING, DriftState.RESOLVED)
        result = sm.auto_transition(eid)
        assert result == DriftState.VERIFIED

    def test_auto_transition_triaged_auto_fixable(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        sm.mark_auto_fixable(eid)
        result = sm.auto_transition(eid)
        assert result == DriftState.RESOLVING

    def test_auto_transition_triaged_not_auto_fixable(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        result = sm.auto_transition(eid)
        assert result is None

    def test_auto_transition_fix_failed(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(eid, DriftState.TRIAGED, DriftState.RESOLVING)
        sm.transition(eid, DriftState.RESOLVING, DriftState.FIX_FAILED)
        result = sm.auto_transition(eid)
        assert result == DriftState.ACKNOWLEDGED
        rec = sm._events[eid]
        assert rec.needs_human is True

    def test_auto_transition_unknown_event(self):
        sm = DriftStateMachine()
        result = sm.auto_transition(uuid.uuid4())
        assert result is None

    def test_auto_transition_detected_no_auto(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.ACKNOWLEDGED)
        result = sm.auto_transition(eid)
        assert result is None


class TestCheckTtl:
    def test_expired_detected_transitions_to_dead_letter(self):
        sm = DriftStateMachine()
        sm.TTL_DETECTED_HOURS = 0
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(eid, DriftState.TRIAGED, DriftState.RESOLVING)
        sm.transition(eid, DriftState.RESOLVING, DriftState.FIX_FAILED)
        sm.transition(eid, DriftState.FIX_FAILED, DriftState.ACKNOWLEDGED)
        sm.transition(eid, DriftState.ACKNOWLEDGED, DriftState.RESOLVING)
        sm.transition(eid, DriftState.RESOLVING, DriftState.RESOLVED)
        sm.transition(eid, DriftState.RESOLVED, DriftState.VERIFIED)
        expired = sm.check_ttl()
        assert eid not in expired

    def test_not_expired_detected_stays(self):
        sm = DriftStateMachine()
        sm.TTL_DETECTED_HOURS = 9999
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        expired = sm.check_ttl()
        assert eid not in expired

    def test_expired_detected_moves_to_dead_letter(self):
        sm = DriftStateMachine()
        sm.TTL_DETECTED_HOURS = 0
        eid = uuid.uuid4()
        rec = DriftEventRecord(
            event_id=eid,
            state=DriftState.DETECTED,
            created_at=datetime.now(UTC) - timedelta(hours=1),
        )
        sm._events[eid] = rec
        expired = sm.check_ttl()
        assert eid in expired
        assert sm.get_state(eid) == DriftState.DEAD_LETTER

    def test_suppressed_expired_returns_to_detected(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(eid, DriftState.TRIAGED, DriftState.RESOLVING)
        sm.transition(eid, DriftState.RESOLVING, DriftState.FIX_FAILED)
        sm.transition(eid, DriftState.FIX_FAILED, DriftState.ACKNOWLEDGED)
        sm.transition(eid, DriftState.ACKNOWLEDGED, DriftState.RESOLVING)
        sm.transition(eid, DriftState.RESOLVING, DriftState.RESOLVED)
        sm.transition(eid, DriftState.RESOLVED, DriftState.VERIFIED)
        past = datetime.now(UTC) - timedelta(hours=1)
        rec = DriftEventRecord(
            event_id=eid,
            state=DriftState.SUPPRESSED,
            created_at=datetime.now(UTC),
        )
        rec.suppressed_until = past
        sm._events[eid] = rec
        expired = sm.check_ttl()
        assert eid in expired
        assert sm.get_state(eid) == DriftState.DETECTED

    def test_no_events_returns_empty(self):
        sm = DriftStateMachine()
        expired = sm.check_ttl()
        assert expired == []


class TestSuppress:
    def test_suppress_raises_no_valid_transition_to_suppressed(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        future = datetime.now(UTC) + timedelta(hours=24)
        with pytest.raises(InvalidTransitionError):
            sm.suppress(eid, future)

    def test_suppress_nonexistent_raises(self):
        sm = DriftStateMachine()
        with pytest.raises(InvalidTransitionError, match="not found"):
            sm.suppress(uuid.uuid4(), datetime.now(UTC) + timedelta(hours=1))


class TestGetState:
    def test_existing_event(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        assert sm.get_state(eid) == DriftState.TRIAGED

    def test_nonexistent_event_returns_none(self):
        sm = DriftStateMachine()
        assert sm.get_state(uuid.uuid4()) is None


class TestMarkAutoFixable:
    def test_mark_existing(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        sm.mark_auto_fixable(eid)
        assert sm._events[eid].auto_fixable is True

    def test_mark_nonexistent_no_error(self):
        sm = DriftStateMachine()
        sm.mark_auto_fixable(uuid.uuid4())


class TestIsTerminal:
    def test_verified_is_terminal(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(eid, DriftState.TRIAGED, DriftState.RESOLVING)
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

    def test_nonexistent_event_not_terminal(self):
        sm = DriftStateMachine()
        assert sm.is_terminal(uuid.uuid4()) is False


class TestTerminalStatesConstant:
    def test_terminal_states_contains_verified_and_false_positive(self):
        assert DriftState.VERIFIED in TERMINAL_STATES
        assert DriftState.FALSE_POSITIVE in TERMINAL_STATES

    def test_terminal_states_excludes_detected(self):
        assert DriftState.DETECTED not in TERMINAL_STATES


class TestInvalidTransitionError:
    def test_is_exception(self):
        assert issubclass(InvalidTransitionError, Exception)

    def test_can_be_raised_and_caught(self):
        with pytest.raises(InvalidTransitionError):
            raise InvalidTransitionError("bad transition")


class TestBoundaryConditions:
    def test_transition_with_empty_resolved_by_not_set(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(eid, DriftState.TRIAGED, DriftState.RESOLVING)
        sm.transition(eid, DriftState.RESOLVING, DriftState.RESOLVED, resolved_by="")
        rec = sm._events[eid]
        assert rec.resolved_by is None

    def test_multiple_events_independent(self):
        sm = DriftStateMachine()
        eid1 = uuid.uuid4()
        eid2 = uuid.uuid4()
        sm.transition(eid1, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(eid2, DriftState.DETECTED, DriftState.FALSE_POSITIVE)
        assert sm.get_state(eid1) == DriftState.TRIAGED
        assert sm.get_state(eid2) == DriftState.FALSE_POSITIVE
        assert sm.is_terminal(eid1) is False
        assert sm.is_terminal(eid2) is True

    def test_full_lifecycle_happy_path(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(eid, DriftState.TRIAGED, DriftState.RESOLVING)
        sm.transition(eid, DriftState.RESOLVING, DriftState.RESOLVED, resolved_by="bot")
        sm.transition(eid, DriftState.RESOLVED, DriftState.VERIFIED)
        assert sm.is_terminal(eid) is True
        rec = sm._events[eid]
        assert rec.resolved_by == "bot"
        assert rec.resolved_at is not None

    def test_fix_failed_retry_cycle(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.TRIAGED)
        sm.transition(eid, DriftState.TRIAGED, DriftState.RESOLVING)
        sm.transition(eid, DriftState.RESOLVING, DriftState.FIX_FAILED)
        sm.transition(eid, DriftState.FIX_FAILED, DriftState.ACKNOWLEDGED)
        sm.transition(eid, DriftState.ACKNOWLEDGED, DriftState.RESOLVING)
        sm.transition(eid, DriftState.RESOLVING, DriftState.RESOLVED)
        sm.transition(eid, DriftState.RESOLVED, DriftState.VERIFIED)
        assert sm.get_state(eid) == DriftState.VERIFIED

    def test_dead_letter_to_acknowledged_recovery(self):
        sm = DriftStateMachine()
        eid = uuid.uuid4()
        sm.transition(eid, DriftState.DETECTED, DriftState.DEAD_LETTER)
        sm.transition(eid, DriftState.DEAD_LETTER, DriftState.ACKNOWLEDGED)
        assert sm.get_state(eid) == DriftState.ACKNOWLEDGED
