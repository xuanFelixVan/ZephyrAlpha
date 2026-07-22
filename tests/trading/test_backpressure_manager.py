# [A_test] module_id: MOD-GOV_backpressure_manager | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] tests.test_backpressure_manager
# [INVARIANTS] BackpressureManager state transitions must be PAUSED/THROTTLED→NORMAL via resume; is_blocked auto-resumes on timeout
# [MODIFY-GUARD] zephyr.infrastructure.pipeline.backpressure_manager
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.raises on invalid input
# [TESTS] —
# [TTL] task_bound

import time

from zephyr.infrastructure.pipeline.backpressure_manager import (
    BackpressureManager,
    BpState,
    BpSymbolState,
    emit_pause,
    emit_resume,
    emit_throttle,
)
from zephyr.infrastructure.pipeline.backpressure_types import (
    BackpressurePause,
    BackpressureResume,
    BackpressureThrottle,
)


class TestBpState:
    def test_enum_values(self):
        assert BpState.NORMAL == "normal"
        assert BpState.PAUSED == "paused"
        assert BpState.THROTTLED == "throttled"

    def test_is_str_enum(self):
        assert isinstance(BpState.NORMAL, str)


class TestBpSymbolState:
    def test_defaults(self):
        s = BpSymbolState(symbol="BTC-PERP")
        assert s.state == BpState.NORMAL
        assert s.max_rate_per_sec == 0
        assert s.paused_until == 0.0
        assert s.paused_at == ""
        assert s.reason == ""
        assert s.signal_id == ""

    def test_with_values(self):
        s = BpSymbolState(
            symbol="ETH-PERP",
            state=BpState.PAUSED,
            reason="overload",
            signal_id="sig-1",
        )
        assert s.symbol == "ETH-PERP"
        assert s.state == BpState.PAUSED
        assert s.reason == "overload"


class TestBackpressureManagerHandlePause:
    def test_handle_pause_sets_state(self):
        mgr = BackpressureManager()
        signal = BackpressurePause(
            signal_id="sig-001",
            symbol="BTC-PERP",
            duration_ms=5000,
            reason="queue overload",
            idempotency_key="key-001",
        )
        state = mgr.handle_pause(signal)
        assert state.state == BpState.PAUSED
        assert state.symbol == "BTC-PERP"
        assert state.reason == "queue overload"
        assert state.signal_id == "sig-001"
        assert state.paused_until > 0

    def test_handle_pause_tracks_in_get_all_paused(self):
        mgr = BackpressureManager()
        signal = BackpressurePause(
            signal_id="sig-001",
            symbol="BTC-PERP",
            duration_ms=5000,
            reason="overload",
            idempotency_key="key-001",
        )
        mgr.handle_pause(signal)
        paused = mgr.get_all_paused()
        assert len(paused) == 1
        assert paused[0].symbol == "BTC-PERP"

    def test_handle_pause_updates_stats(self):
        mgr = BackpressureManager()
        signal = BackpressurePause(
            signal_id="sig-001",
            symbol="BTC-PERP",
            duration_ms=5000,
            reason="overload",
            idempotency_key="key-001",
        )
        mgr.handle_pause(signal)
        stats = mgr.get_stats()
        assert stats["paused_count"] == 1
        assert stats["total_tracked_symbols"] == 1
        assert stats["total_events"] == 1


class TestBackpressureManagerHandleThrottle:
    def test_handle_throttle_sets_state(self):
        mgr = BackpressureManager()
        signal = BackpressureThrottle(
            signal_id="sig-002",
            symbol="ETH-PERP",
            max_rate_per_sec=10,
            reason="queue buildup",
            idempotency_key="key-002",
        )
        state = mgr.handle_throttle(signal)
        assert state.state == BpState.THROTTLED
        assert state.max_rate_per_sec == 10
        assert state.reason == "queue buildup"

    def test_handle_throttle_tracks_in_get_all_throttled(self):
        mgr = BackpressureManager()
        signal = BackpressureThrottle(
            signal_id="sig-002",
            symbol="ETH-PERP",
            max_rate_per_sec=10,
            reason="buildup",
            idempotency_key="key-002",
        )
        mgr.handle_throttle(signal)
        throttled = mgr.get_all_throttled()
        assert len(throttled) == 1
        assert throttled[0].symbol == "ETH-PERP"


class TestBackpressureManagerHandleResume:
    def test_handle_resume_resets_state(self):
        mgr = BackpressureManager()
        pause_signal = BackpressurePause(
            signal_id="sig-001",
            symbol="BTC-PERP",
            duration_ms=5000,
            reason="overload",
            idempotency_key="key-001",
        )
        mgr.handle_pause(pause_signal)
        resume_signal = BackpressureResume(
            signal_id="sig-003",
            symbol="BTC-PERP",
            reason="recovered",
            idempotency_key="key-003",
        )
        state = mgr.handle_resume(resume_signal)
        assert state.state == BpState.NORMAL
        assert state.max_rate_per_sec == 0
        assert state.paused_until == 0.0
        assert state.reason == "recovered"

    def test_handle_resume_clears_paused_list(self):
        mgr = BackpressureManager()
        pause_signal = BackpressurePause(
            signal_id="sig-001",
            symbol="BTC-PERP",
            duration_ms=5000,
            reason="overload",
            idempotency_key="key-001",
        )
        mgr.handle_pause(pause_signal)
        resume_signal = BackpressureResume(
            signal_id="sig-003",
            symbol="BTC-PERP",
            reason="recovered",
            idempotency_key="key-003",
        )
        mgr.handle_resume(resume_signal)
        assert mgr.get_all_paused() == []


class TestBackpressureManagerIsBlocked:
    def test_is_blocked_when_paused(self):
        mgr = BackpressureManager()
        signal = BackpressurePause(
            signal_id="sig-001",
            symbol="BTC-PERP",
            duration_ms=60000,
            reason="overload",
            idempotency_key="key-001",
        )
        mgr.handle_pause(signal)
        assert mgr.is_blocked("BTC-PERP") is True

    def test_is_not_blocked_when_normal(self):
        mgr = BackpressureManager()
        assert mgr.is_blocked("BTC-PERP") is False

    def test_is_not_blocked_when_throttled(self):
        mgr = BackpressureManager()
        signal = BackpressureThrottle(
            signal_id="sig-002",
            symbol="BTC-PERP",
            max_rate_per_sec=10,
            reason="buildup",
            idempotency_key="key-002",
        )
        mgr.handle_throttle(signal)
        assert mgr.is_blocked("BTC-PERP") is False

    def test_auto_resume_on_timeout(self):
        mgr = BackpressureManager()
        signal = BackpressurePause(
            signal_id="sig-001",
            symbol="BTC-PERP",
            duration_ms=1,
            reason="overload",
            idempotency_key="key-001",
        )
        mgr.handle_pause(signal)
        time.sleep(0.01)
        assert mgr.is_blocked("BTC-PERP") is False
        state = mgr.get_state("BTC-PERP")
        assert state.state == BpState.NORMAL


class TestBackpressureManagerGetState:
    def test_get_state_unknown_symbol(self):
        mgr = BackpressureManager()
        state = mgr.get_state("UNKNOWN")
        assert state.symbol == "UNKNOWN"
        assert state.state == BpState.NORMAL

    def test_get_state_known_symbol(self):
        mgr = BackpressureManager()
        signal = BackpressurePause(
            signal_id="sig-001",
            symbol="BTC-PERP",
            duration_ms=5000,
            reason="overload",
            idempotency_key="key-001",
        )
        mgr.handle_pause(signal)
        state = mgr.get_state("BTC-PERP")
        assert state.state == BpState.PAUSED


class TestBackpressureManagerCallbacks:
    def test_register_on_pause(self):
        mgr = BackpressureManager()
        received = []
        mgr.register_on_pause(lambda s: received.append(s.symbol))
        signal = BackpressurePause(
            signal_id="sig-001",
            symbol="BTC-PERP",
            duration_ms=5000,
            reason="overload",
            idempotency_key="key-001",
        )
        mgr.handle_pause(signal)
        assert received == ["BTC-PERP"]

    def test_register_on_resume(self):
        mgr = BackpressureManager()
        received = []
        mgr.register_on_resume(lambda s: received.append(s.symbol))
        pause_signal = BackpressurePause(
            signal_id="sig-001",
            symbol="BTC-PERP",
            duration_ms=5000,
            reason="overload",
            idempotency_key="key-001",
        )
        mgr.handle_pause(pause_signal)
        resume_signal = BackpressureResume(
            signal_id="sig-003",
            symbol="BTC-PERP",
            reason="recovered",
            idempotency_key="key-003",
        )
        mgr.handle_resume(resume_signal)
        assert received == ["BTC-PERP"]

    def test_register_on_throttle(self):
        mgr = BackpressureManager()
        received = []
        mgr.register_on_throttle(lambda s: received.append(s.symbol))
        signal = BackpressureThrottle(
            signal_id="sig-002",
            symbol="ETH-PERP",
            max_rate_per_sec=10,
            reason="buildup",
            idempotency_key="key-002",
        )
        mgr.handle_throttle(signal)
        assert received == ["ETH-PERP"]

    def test_callback_exception_does_not_propagate(self):
        mgr = BackpressureManager()
        mgr.register_on_pause(lambda s: 1 / 0)
        signal = BackpressurePause(
            signal_id="sig-001",
            symbol="BTC-PERP",
            duration_ms=5000,
            reason="overload",
            idempotency_key="key-001",
        )
        state = mgr.handle_pause(signal)
        assert state.state == BpState.PAUSED


class TestBackpressureManagerClear:
    def test_clear_resets_all(self):
        mgr = BackpressureManager()
        signal = BackpressurePause(
            signal_id="sig-001",
            symbol="BTC-PERP",
            duration_ms=5000,
            reason="overload",
            idempotency_key="key-001",
        )
        mgr.handle_pause(signal)
        mgr.register_on_pause(lambda s: None)
        mgr.clear()
        stats = mgr.get_stats()
        assert stats["total_tracked_symbols"] == 0
        assert stats["total_events"] == 0


class TestBackpressureManagerGetStats:
    def test_empty_stats(self):
        mgr = BackpressureManager()
        stats = mgr.get_stats()
        assert stats["total_tracked_symbols"] == 0
        assert stats["paused_count"] == 0
        assert stats["throttled_count"] == 0
        assert stats["normal_count"] == 0
        assert stats["total_events"] == 0

    def test_mixed_states_stats(self):
        mgr = BackpressureManager()
        mgr.handle_pause(
            BackpressurePause(
                signal_id="s1",
                symbol="A",
                duration_ms=5000,
                reason="r",
                idempotency_key="k1",
            )
        )
        mgr.handle_throttle(
            BackpressureThrottle(
                signal_id="s2",
                symbol="B",
                max_rate_per_sec=10,
                reason="r",
                idempotency_key="k2",
            )
        )
        stats = mgr.get_stats()
        assert stats["paused_count"] == 1
        assert stats["throttled_count"] == 1
        assert stats["normal_count"] == 0
        assert stats["total_events"] == 2


class TestEmitHelpers:
    def test_emit_pause(self):
        mgr = BackpressureManager()
        state = emit_pause(mgr, "BTC-PERP", 5000, "overload")
        assert state.state == BpState.PAUSED
        assert state.symbol == "BTC-PERP"
        assert state.reason == "overload"

    def test_emit_throttle(self):
        mgr = BackpressureManager()
        state = emit_throttle(mgr, "ETH-PERP", 10, "buildup")
        assert state.state == BpState.THROTTLED
        assert state.max_rate_per_sec == 10

    def test_emit_resume(self):
        mgr = BackpressureManager()
        emit_pause(mgr, "BTC-PERP", 5000, "overload")
        state = emit_resume(mgr, "BTC-PERP", "recovered")
        assert state.state == BpState.NORMAL
        assert state.reason == "recovered"

    def test_emit_pause_generates_signal_id(self):
        mgr = BackpressureManager()
        state = emit_pause(mgr, "BTC-PERP", 5000, "overload")
        assert state.signal_id.startswith("bps-")

    def test_emit_throttle_generates_signal_id(self):
        mgr = BackpressureManager()
        state = emit_throttle(mgr, "ETH-PERP", 10, "buildup")
        assert state.signal_id.startswith("bps-")

    def test_emit_resume_generates_signal_id(self):
        mgr = BackpressureManager()
        state = emit_resume(mgr, "BTC-PERP", "recovered")
        assert state.signal_id.startswith("bps-")
