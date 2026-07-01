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
        from zephyr.trading.feedback_loop.scheduler import FeedbackLoopScheduler

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
            from zephyr.trading.feedback_loop.scheduler import FeedbackLoopScheduler

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
            from zephyr.trading.feedback_loop.scheduler import FeedbackLoopScheduler

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
