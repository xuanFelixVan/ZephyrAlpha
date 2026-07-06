# [A_test] module_id: SRC-TST-2136 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §3.1
# [MODULE] tests.test_trading_session_lifecycle
# [CONSUMERS] zephyr.trading.session_lifecycle
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] task_bound
"""tests.test_trading_session_lifecycle — F1 SessionLifecycle 测试

覆盖 trading/session_lifecycle.py 的核心接口：
- SessionState / SessionTransition / SessionTrustTier 枚举
- SESSION_TRANSITIONS 状态机映射
- SessionStateRecord / GCStats 数据模型
- _compute_trust_tier 信任分级
- SessionLifecycle: register/transition/get_state/update_trust/increment_violation/close/gc/health_check
"""
from __future__ import annotations

import time

import pytest

from zephyr.governance.behavioral_admission.session_lifecycle import (
    GCStats,
    SESSION_TRANSITIONS,
    SessionLifecycle,
    SessionState,
    SessionStateRecord,
    SessionTransition,
    SessionTrustTier,
    _compute_trust_tier,
)
from zephyr.shared.foundation.errors import SessionError


class TestSessionStateEnum:
    def test_enum_values(self):
        assert SessionState.ACTIVE.value == "ACTIVE"
        assert SessionState.IDLE.value == "IDLE"
        assert SessionState.CLOSED.value == "CLOSED"
        assert SessionState.EXPIRED.value == "EXPIRED"
        assert SessionState.RESPONDING.value == "RESPONDING"
        assert SessionState.DEGRADED.value == "DEGRADED"

    def test_enum_count(self):
        assert len(SessionState) == 6


class TestSessionTransitionEnum:
    def test_enum_values(self):
        assert SessionTransition.ACTIVATE.value == "ACTIVATE"
        assert SessionTransition.IDLE.value == "IDLE"
        assert SessionTransition.RESUME.value == "RESUME"
        assert SessionTransition.CLOSE.value == "CLOSE"
        assert SessionTransition.EXPIRE.value == "EXPIRE"
        assert SessionTransition.DEGRADE.value == "DEGRADE"
        assert SessionTransition.RECOVER.value == "RECOVER"
        assert SessionTransition.RESPOND.value == "RESPOND"
        assert SessionTransition.COMPLETE.value == "COMPLETE"

    def test_enum_count(self):
        assert len(SessionTransition) == 9


class TestSessionTransitionsMap:
    def test_active_transitions(self):
        allowed = SESSION_TRANSITIONS[SessionState.ACTIVE]
        assert SessionTransition.IDLE in allowed
        assert SessionTransition.CLOSE in allowed
        assert SessionTransition.DEGRADE in allowed
        assert SessionTransition.RESPOND in allowed

    def test_expired_is_terminal(self):
        assert SESSION_TRANSITIONS[SessionState.EXPIRED] == {}

    def test_closed_only_expire(self):
        allowed = SESSION_TRANSITIONS[SessionState.CLOSED]
        assert SessionTransition.EXPIRE in allowed
        assert len(allowed) == 1


class TestSessionTrustTierEnum:
    def test_enum_values(self):
        assert SessionTrustTier.PLATINUM.value == "PLATINUM"
        assert SessionTrustTier.GOLD.value == "GOLD"
        assert SessionTrustTier.SILVER.value == "SILVER"
        assert SessionTrustTier.BRONZE.value == "BRONZE"
        assert SessionTrustTier.REVOKED.value == "REVOKED"

    def test_enum_count(self):
        assert len(SessionTrustTier) == 5


class TestComputeTrustTier:
    def test_platinum(self):
        assert _compute_trust_tier(95.0) == SessionTrustTier.PLATINUM
        assert _compute_trust_tier(90.0) == SessionTrustTier.PLATINUM

    def test_gold(self):
        assert _compute_trust_tier(89.9) == SessionTrustTier.GOLD
        assert _compute_trust_tier(70.0) == SessionTrustTier.GOLD

    def test_silver(self):
        assert _compute_trust_tier(69.9) == SessionTrustTier.SILVER
        assert _compute_trust_tier(40.0) == SessionTrustTier.SILVER

    def test_bronze(self):
        assert _compute_trust_tier(39.9) == SessionTrustTier.BRONZE
        assert _compute_trust_tier(10.0) == SessionTrustTier.BRONZE

    def test_revoked(self):
        assert _compute_trust_tier(9.9) == SessionTrustTier.REVOKED
        assert _compute_trust_tier(0.0) == SessionTrustTier.REVOKED


class TestSessionStateRecord:
    def test_defaults(self):
        record = SessionStateRecord(session_id="s1")
        assert record.session_id == "s1"
        assert record.state == SessionState.ACTIVE
        assert record.trust_score == 50.0
        assert record.violation_count == 0
        assert record.trust_tier == SessionTrustTier.SILVER
        assert record.transition_history == []

    def test_extra_forbidden(self):
        with pytest.raises(Exception):
            SessionStateRecord(session_id="s1", unknown_field="x")


class TestGCStats:
    def test_defaults(self):
        stats = GCStats()
        assert stats.total_gc_runs == 0
        assert stats.expired_sessions == 0
        assert stats.last_gc_time == 0.0


class TestSessionLifecycleInit:
    def test_init_with_memory_db(self):
        sl = SessionLifecycle(db_path=":memory:")
        assert sl._db_path == ":memory:"
        assert sl._max_active_sessions == 100

    def test_init_custom_params(self):
        sl = SessionLifecycle(
            db_path=":memory:",
            idle_timeout_s=600,
            closed_expiry_s=3600,
            gc_interval_s=60,
            max_active_sessions=10,
        )
        assert sl._idle_timeout_s == 600
        assert sl._closed_expiry_s == 3600
        assert sl._gc_interval_s == 60
        assert sl._max_active_sessions == 10


class TestRegisterSession:
    def test_register_new_session(self):
        sl = SessionLifecycle(db_path=":memory:")
        record = sl.register_session("s1")
        assert record.session_id == "s1"
        assert record.state == SessionState.ACTIVE
        assert record.trust_score == 50.0
        assert record.trust_tier == SessionTrustTier.SILVER
        assert len(record.transition_history) == 1
        assert record.transition_history[0]["from"] == "NONE"
        assert record.transition_history[0]["to"] == "ACTIVE"

    def test_register_idempotent(self):
        sl = SessionLifecycle(db_path=":memory:")
        r1 = sl.register_session("s1")
        r2 = sl.register_session("s1")
        assert r1 is r2

    def test_register_capacity_exceeded(self):
        sl = SessionLifecycle(db_path=":memory:", max_active_sessions=1)
        sl.register_session("s1")
        with pytest.raises(RuntimeError, match="max_active_sessions"):
            sl.register_session("s2")


class TestTransition:
    def test_valid_transition_active_to_idle(self):
        sl = SessionLifecycle(db_path=":memory:")
        sl.register_session("s1")
        new_state = sl.transition("s1", SessionTransition.IDLE)
        assert new_state == SessionState.IDLE

    def test_valid_transition_idle_to_active(self):
        sl = SessionLifecycle(db_path=":memory:")
        sl.register_session("s1")
        sl.transition("s1", SessionTransition.IDLE)
        new_state = sl.transition("s1", SessionTransition.RESUME)
        assert new_state == SessionState.ACTIVE

    def test_invalid_transition(self):
        sl = SessionLifecycle(db_path=":memory:")
        sl.register_session("s1")
        sl.transition("s1", SessionTransition.CLOSE)
        with pytest.raises(SessionError, match="invalid transition"):
            sl.transition("s1", SessionTransition.IDLE)

    def test_transition_unknown_session(self):
        sl = SessionLifecycle(db_path=":memory:")
        with pytest.raises(SessionError, match="session not found"):
            sl.transition("unknown", SessionTransition.IDLE)

    def test_transition_records_history(self):
        sl = SessionLifecycle(db_path=":memory:")
        sl.register_session("s1")
        sl.transition("s1", SessionTransition.IDLE)
        record = sl.get_state("s1")
        assert len(record.transition_history) == 2
        assert record.transition_history[1]["from"] == "ACTIVE"
        assert record.transition_history[1]["to"] == "IDLE"


class TestGetState:
    def test_get_existing_session(self):
        sl = SessionLifecycle(db_path=":memory:")
        sl.register_session("s1")
        record = sl.get_state("s1")
        assert record is not None
        assert record.session_id == "s1"

    def test_get_nonexistent_session(self):
        sl = SessionLifecycle(db_path=":memory:")
        assert sl.get_state("unknown") is None


class TestGetTrustTier:
    def test_get_trust_tier_existing(self):
        sl = SessionLifecycle(db_path=":memory:")
        sl.register_session("s1")
        assert sl.get_trust_tier("s1") == SessionTrustTier.SILVER

    def test_get_trust_tier_nonexistent(self):
        sl = SessionLifecycle(db_path=":memory:")
        assert sl.get_trust_tier("unknown") == SessionTrustTier.REVOKED


class TestUpdateTrustScore:
    def test_increase_score(self):
        sl = SessionLifecycle(db_path=":memory:")
        sl.register_session("s1")
        new_score = sl.update_trust_score("s1", 30.0)
        assert new_score == 80.0
        assert sl.get_state("s1").trust_tier == SessionTrustTier.GOLD

    def test_decrease_score(self):
        sl = SessionLifecycle(db_path=":memory:")
        sl.register_session("s1")
        new_score = sl.update_trust_score("s1", -20.0)
        assert new_score == 30.0
        assert sl.get_state("s1").trust_tier == SessionTrustTier.BRONZE

    def test_score_clamped_to_100(self):
        sl = SessionLifecycle(db_path=":memory:")
        sl.register_session("s1")
        new_score = sl.update_trust_score("s1", 100.0)
        assert new_score == 100.0

    def test_score_clamped_to_0(self):
        sl = SessionLifecycle(db_path=":memory:")
        sl.register_session("s1")
        new_score = sl.update_trust_score("s1", -100.0)
        assert new_score == 0.0

    def test_update_unknown_session(self):
        sl = SessionLifecycle(db_path=":memory:")
        with pytest.raises(SessionError, match="session not found"):
            sl.update_trust_score("unknown", 10.0)


class TestIncrementViolation:
    def test_first_violation(self):
        sl = SessionLifecycle(db_path=":memory:")
        sl.register_session("s1")
        count = sl.increment_violation("s1")
        assert count == 1
        record = sl.get_state("s1")
        assert record.violation_count == 1
        assert record.trust_score == 49.0

    def test_multiple_violations(self):
        sl = SessionLifecycle(db_path=":memory:")
        sl.register_session("s1")
        sl.increment_violation("s1")
        sl.increment_violation("s1")
        count = sl.increment_violation("s1")
        assert count == 3
        record = sl.get_state("s1")
        # 50 - 1 - 2 - 3 = 44
        assert record.trust_score == 44.0

    def test_violation_unknown_session(self):
        sl = SessionLifecycle(db_path=":memory:")
        with pytest.raises(SessionError, match="session not found"):
            sl.increment_violation("unknown")


class TestCloseSession:
    def test_close_active_session(self):
        sl = SessionLifecycle(db_path=":memory:")
        sl.register_session("s1")
        result = sl.close_session("s1")
        assert result is True
        assert sl.get_state("s1").state == SessionState.CLOSED

    def test_close_already_closed(self):
        sl = SessionLifecycle(db_path=":memory:")
        sl.register_session("s1")
        sl.close_session("s1")
        result = sl.close_session("s1")
        assert result is True

    def test_close_unknown_session(self):
        sl = SessionLifecycle(db_path=":memory:")
        result = sl.close_session("unknown")
        assert result is False


class TestRunGc:
    def test_gc_no_sessions(self):
        sl = SessionLifecycle(db_path=":memory:")
        expired = sl.run_gc()
        assert expired == 0

    def test_gc_idle_timeout(self):
        sl = SessionLifecycle(db_path=":memory:", idle_timeout_s=0)
        sl.register_session("s1")
        sl.transition("s1", SessionTransition.IDLE)
        time.sleep(0.01)
        expired = sl.run_gc()
        assert expired == 1
        assert sl.get_state("s1").state == SessionState.EXPIRED

    def test_gc_closed_expiry(self):
        sl = SessionLifecycle(db_path=":memory:", closed_expiry_s=0)
        sl.register_session("s1")
        sl.close_session("s1")
        time.sleep(0.01)
        expired = sl.run_gc()
        assert expired == 1
        assert sl.get_state("s1").state == SessionState.EXPIRED

    def test_gc_updates_stats(self):
        sl = SessionLifecycle(db_path=":memory:", idle_timeout_s=0)
        sl.register_session("s1")
        sl.transition("s1", SessionTransition.IDLE)
        time.sleep(0.01)
        sl.run_gc()
        stats = sl.get_gc_stats()
        assert stats.total_gc_runs == 1
        assert stats.expired_sessions == 1
        assert stats.idle_to_expired == 1


class TestGetActiveSessions:
    def test_empty(self):
        sl = SessionLifecycle(db_path=":memory:")
        assert sl.get_active_sessions() == []

    def test_with_sessions(self):
        sl = SessionLifecycle(db_path=":memory:")
        sl.register_session("s1")
        sl.register_session("s2")
        active = sl.get_active_sessions()
        assert len(active) == 2

    def test_excludes_closed(self):
        sl = SessionLifecycle(db_path=":memory:")
        sl.register_session("s1")
        sl.close_session("s1")
        active = sl.get_active_sessions()
        assert len(active) == 0


class TestHealthCheck:
    def test_healthy(self):
        sl = SessionLifecycle(db_path=":memory:")
        sl.register_session("s1")
        health = sl.health_check()
        assert health["status"] == "healthy"
        assert health["total_sessions"] == 1
        assert health["active_sessions"] == 1

    def test_at_capacity(self):
        sl = SessionLifecycle(db_path=":memory:", max_active_sessions=1)
        sl.register_session("s1")
        health = sl.health_check()
        assert health["status"] == "at_capacity"
        assert health["max_active_sessions"] == 1


class TestRestoreFromDb:
    def test_restore_existing_in_memory(self):
        sl = SessionLifecycle(db_path=":memory:")
        sl.register_session("s1")
        record = sl.restore_from_db("s1")
        assert record is not None
        assert record.session_id == "s1"

    def test_restore_nonexistent(self):
        sl = SessionLifecycle(db_path=":memory:")
        record = sl.restore_from_db("unknown")
        assert record is None
