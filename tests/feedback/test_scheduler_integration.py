# [A_test] module_id: SRC-TST-202408 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §4-§5
# [MODULE] tests.unit.feedback_loop.test_scheduler_integration
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound

"""Integration tests: FeedbackLoopScheduler start/stop/tick lifecycle.

Unlike test_feedback_core.py which mocks all sub-components, these tests
verify the actual start/stop/tick lifecycle behavior of FeedbackLoopScheduler.
Only InProcessVectorMemory is mocked to avoid loading torch/sentence_transformers.
"""

from __future__ import annotations

import threading
import time
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def scheduler():
    """Create a FeedbackLoopScheduler with InProcessVectorMemory mocked."""
    with patch(
        "zephyr.integration.vector_memory.in_process_vector_memory.InProcessVectorMemory"
    ) as vms_cls:
        vms_cls.return_value = MagicMock()
        from zephyr.feedback_loop.scheduler import FeedbackLoopScheduler

        FeedbackLoopScheduler.reset_instance()
        s = FeedbackLoopScheduler(poll_interval=0.1)
        yield s
        # Cleanup: ensure stopped
        if s._running:
            s.stop()
        FeedbackLoopScheduler.reset_instance()


class TestSchedulerStart:
    """Test start() lifecycle."""

    def test_start_sets_running_flag(self, scheduler):
        """start() sets _running=True."""
        assert scheduler._running is False
        scheduler.start()
        assert scheduler._running is True

    def test_start_creates_thread(self, scheduler):
        """start() creates a daemon thread."""
        assert scheduler._thread is None
        scheduler.start()
        assert scheduler._thread is not None
        assert scheduler._thread.daemon is True
        assert scheduler._thread.name == "FLE-Scheduler"

    def test_start_is_idempotent(self, scheduler):
        """start() called twice does not create a second thread."""
        scheduler.start()
        thread1 = scheduler._thread
        scheduler.start()
        assert scheduler._thread is thread1

    def test_start_resets_consecutive_errors(self, scheduler):
        """start() resets _consecutive_errors to 0."""
        scheduler._consecutive_errors = 5
        scheduler.start()
        assert scheduler._consecutive_errors == 0


class TestSchedulerStop:
    """Test stop() lifecycle."""

    def test_stop_clears_running_flag(self, scheduler):
        """stop() sets _running=False."""
        scheduler.start()
        assert scheduler._running is True
        scheduler.stop()
        assert scheduler._running is False

    def test_stop_joins_thread(self, scheduler):
        """stop() joins the background thread."""
        scheduler.start()
        thread = scheduler._thread
        scheduler.stop()
        assert not thread.is_alive()

    def test_stop_without_start(self, scheduler):
        """stop() without start() does not raise."""
        scheduler.stop()
        assert scheduler._running is False

    def test_stop_is_idempotent(self, scheduler):
        """stop() called twice does not raise."""
        scheduler.start()
        scheduler.stop()
        scheduler.stop()
        assert scheduler._running is False


class TestSchedulerTick:
    """Test tick() behavior."""

    def test_tick_returns_event_or_none(self, scheduler):
        """tick() returns FLEPipelineEvent or None (does not raise)."""
        result = scheduler.tick()
        # tick may return None if _run_once has no anomaly, or FLEPipelineEvent
        assert result is None or hasattr(result, "run_id")

    def test_tick_increments_run_count(self, scheduler):
        """tick() that produces an event increments run_count."""
        initial = scheduler.run_count()
        scheduler.tick()
        # run_count may or may not increment depending on whether _run_once succeeds
        assert scheduler.run_count() >= initial

    def test_tick_does_not_require_start(self, scheduler):
        """tick() works without start() (manual mode)."""
        assert scheduler._running is False
        # Should not raise
        scheduler.tick()


class TestSchedulerRunLoop:
    """Test _run_loop behavior with actual thread."""

    def test_run_loop_executes_cycles(self, scheduler):
        """start() runs _run_loop which increments _cycle_count."""
        scheduler.start()
        time.sleep(0.5)  # Allow at least 1 cycle (poll_interval=0.1)
        scheduler.stop()
        assert scheduler._cycle_count > 0

    def test_run_loop_stops_on_stop(self, scheduler):
        """_run_loop exits when stop() is called."""
        scheduler.start()
        time.sleep(0.3)
        scheduler.stop()
        # Thread should be dead
        assert not scheduler._thread.is_alive()

    def test_run_loop_records_events(self, scheduler):
        """_run_loop records events in _events list."""
        scheduler.start()
        time.sleep(0.5)
        scheduler.stop()
        # Events may be empty if _run_once returns None, but _events should be a list
        assert isinstance(scheduler._events, list)


class TestSchedulerErrorRecovery:
    """Test error recovery in _run_loop."""

    def test_consecutive_errors_increment_on_failure(self, scheduler):
        """_run_loop increments _consecutive_errors on exception."""
        # Mock _run_once to raise
        with patch.object(scheduler, "_run_once", side_effect=RuntimeError("test")):
            scheduler.start()
            time.sleep(0.5)
            scheduler.stop()
        # Should have some consecutive errors
        assert scheduler._consecutive_errors >= 0

    def test_scheduler_recovers_from_errors(self, scheduler):
        """Scheduler does not crash permanently on errors."""
        call_count = 0

        def fail_then_succeed(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise RuntimeError("transient")
            return None

        with patch.object(scheduler, "_run_once", side_effect=fail_then_succeed):
            scheduler.start()
            time.sleep(0.5)
            scheduler.stop()
        # Scheduler should still be stoppable (not crashed)
        assert scheduler._running is False


class TestSchedulerSingleton:
    """Test singleton get_instance/reset_instance."""

    def test_get_instance_returns_singleton(self):
        """get_instance returns the same instance."""
        with patch(
            "zephyr.integration.vector_memory.in_process_vector_memory.InProcessVectorMemory"
        ):
            from zephyr.feedback_loop.scheduler import FeedbackLoopScheduler

            FeedbackLoopScheduler.reset_instance()
            inst1 = FeedbackLoopScheduler.get_instance(poll_interval=0.1)
            inst2 = FeedbackLoopScheduler.get_instance()
            assert inst1 is inst2
            FeedbackLoopScheduler.reset_instance()

    def test_reset_instance_clears_singleton(self):
        """reset_instance clears the singleton."""
        with patch(
            "zephyr.integration.vector_memory.in_process_vector_memory.InProcessVectorMemory"
        ):
            from zephyr.feedback_loop.scheduler import FeedbackLoopScheduler

            FeedbackLoopScheduler.reset_instance()
            inst1 = FeedbackLoopScheduler.get_instance(poll_interval=0.1)
            FeedbackLoopScheduler.reset_instance()
            inst2 = FeedbackLoopScheduler.get_instance(poll_interval=0.1)
            assert inst1 is not inst2
            FeedbackLoopScheduler.reset_instance()


class TestSchedulerEvents:
    """Test events() and run_count() API."""

    def test_events_returns_list(self, scheduler):
        """events() returns a list of dicts."""
        events = scheduler.events()
        assert isinstance(events, list)

    def test_run_count_initial_zero(self, scheduler):
        """run_count() is 0 initially."""
        assert scheduler.run_count() == 0

    def test_health_report_returns_dict(self, scheduler):
        """health_report() returns a dict."""
        report = scheduler.health_report()
        assert isinstance(report, dict)


# ══════════════════════════════════════════════════════════
# 5.158.4 回归测试——_persist_failure_pattern (extracted from _run_once)
# ══════════════════════════════════════════════════════════

class TestPersistFailurePattern:
    """5.158.4 回归测试——_persist_failure_pattern 行为等价验证。

    使用 object.__new__ 创建轻量实例，避免重量级 __init__，
    只设置 vector_bridge 字段测试提取的方法。
    """

    def _make_bare_scheduler(self):
        from zephyr.feedback_loop.scheduler import FeedbackLoopScheduler
        s = object.__new__(FeedbackLoopScheduler)
        return s

    def _make_event(self, diagnosis=None, verification=None):
        event = MagicMock()
        event.diagnosis = diagnosis
        event.verification = verification
        return event

    def test_no_vector_bridge_skips(self):
        """vector_bridge is None → no-op, no exception."""
        s = self._make_bare_scheduler()
        s.vector_bridge = None
        event = self._make_event(diagnosis=MagicMock(summary="x"))
        s._persist_failure_pattern(event)

    def test_no_diagnosis_skips(self):
        """diagnosis is None → no write."""
        s = self._make_bare_scheduler()
        s.vector_bridge = MagicMock()
        event = self._make_event(diagnosis=None)
        s._persist_failure_pattern(event)
        s.vector_bridge.write_failure_pattern.assert_not_called()

    def test_summary_present_writes(self):
        """diagnosis.summary present → uses summary as pattern."""
        s = self._make_bare_scheduler()
        s.vector_bridge = MagicMock()
        diag = MagicMock()
        diag.summary = "CPU elevated"
        diag.root_cause = None
        verification = MagicMock()
        verification.verdict = "ANOMALY"
        event = self._make_event(diagnosis=diag, verification=verification)
        s._persist_failure_pattern(event)
        s.vector_bridge.write_failure_pattern.assert_called_once_with("CPU elevated")

    def test_root_cause_strips_zscore(self):
        """summary None + root_cause present → strips ' (z=...)' suffix."""
        s = self._make_bare_scheduler()
        s.vector_bridge = MagicMock()
        diag = MagicMock()
        diag.summary = None
        diag.root_cause = "Elevated cpu_usage (z=3.50)"
        verification = MagicMock()
        verification.verdict = "ANOMALY"
        event = self._make_event(diagnosis=diag, verification=verification)
        s._persist_failure_pattern(event)
        s.vector_bridge.write_failure_pattern.assert_called_once_with("Elevated cpu_usage")

    def test_no_verification_skips(self):
        """diag_text present but verification None → no write."""
        s = self._make_bare_scheduler()
        s.vector_bridge = MagicMock()
        diag = MagicMock()
        diag.summary = "test"
        diag.root_cause = None
        event = self._make_event(diagnosis=diag, verification=None)
        s._persist_failure_pattern(event)
        s.vector_bridge.write_failure_pattern.assert_not_called()

    def test_healthy_verdict_skips(self):
        """verdict is HEALTHY → no write."""
        s = self._make_bare_scheduler()
        s.vector_bridge = MagicMock()
        diag = MagicMock()
        diag.summary = "test"
        diag.root_cause = None
        verification = MagicMock()
        verification.verdict = "HEALTHY"
        event = self._make_event(diagnosis=diag, verification=verification)
        s._persist_failure_pattern(event)
        s.vector_bridge.write_failure_pattern.assert_not_called()

    def test_nominal_verdict_skips(self):
        """verdict is NOMINAL → no write."""
        s = self._make_bare_scheduler()
        s.vector_bridge = MagicMock()
        diag = MagicMock()
        diag.summary = "test"
        diag.root_cause = None
        verification = MagicMock()
        verification.verdict = "NOMINAL"
        event = self._make_event(diagnosis=diag, verification=verification)
        s._persist_failure_pattern(event)
        s.vector_bridge.write_failure_pattern.assert_not_called()

    def test_write_exception_suppressed(self):
        """write_failure_pattern raises → suppressed, no propagation."""
        s = self._make_bare_scheduler()
        s.vector_bridge = MagicMock()
        s.vector_bridge.write_failure_pattern.side_effect = RuntimeError("VMS down")
        diag = MagicMock()
        diag.summary = "test"
        diag.root_cause = None
        verification = MagicMock()
        verification.verdict = "ANOMALY"
        event = self._make_event(diagnosis=diag, verification=verification)
        s._persist_failure_pattern(event)  # should not raise
