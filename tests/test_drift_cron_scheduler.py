# [A_test] module_id: SRC-TST-0771 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md | §
# [MODULE] tests.test_drift_cron_scheduler
# [INVARIANTS] 定期扫描不可禁用
# [MODIFY-GUARD] src/zephyr/behavioral-auditor/drift_cron_scheduler.py
# [CONSUMERS] CI pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip
# [TESTS] python -m pytest tests/test_drift_cron_scheduler.py -q

from __future__ import annotations

from zephyr.behavioral_audit.drift_cron_scheduler import (
    DEEP_INTERVAL_S,
    STANDARD_INTERVAL_S,
    DriftCronScheduler,
    ensure_scheduler_running,
    stop_scheduler,
)


class TestConstants:
    def test_standard_interval(self):
        assert STANDARD_INTERVAL_S == 30 * 60

    def test_deep_interval(self):
        assert DEEP_INTERVAL_S == 6 * 60 * 60

    def test_deep_longer_than_standard(self):
        assert DEEP_INTERVAL_S > STANDARD_INTERVAL_S


class TestDriftCronScheduler:
    def test_init_defaults(self):
        scheduler = DriftCronScheduler()
        assert scheduler._thread is None
        assert scheduler._last_standard is None
        assert scheduler._last_deep is None

    def test_start_creates_thread(self):
        scheduler = DriftCronScheduler()
        scheduler.start()
        assert scheduler._thread is not None
        assert scheduler._thread.daemon is True
        scheduler.stop()

    def test_stop_clears_thread(self):
        scheduler = DriftCronScheduler()
        scheduler.start()
        scheduler.stop()
        assert scheduler._thread is None

    def test_stop_event_is_set_after_stop(self):
        scheduler = DriftCronScheduler()
        scheduler.start()
        scheduler.stop()
        assert scheduler._stop_event.is_set()

    def test_start_idempotent(self):
        scheduler = DriftCronScheduler()
        scheduler.start()
        thread1 = scheduler._thread
        scheduler.start()
        thread2 = scheduler._thread
        assert thread1 is thread2
        scheduler.stop()

    def test_stop_idempotent(self):
        scheduler = DriftCronScheduler()
        scheduler.start()
        scheduler.stop()
        scheduler.stop()
        assert scheduler._thread is None

    def test_start_stop_lifecycle(self):
        scheduler = DriftCronScheduler()
        scheduler.start()
        assert scheduler._thread is not None
        scheduler.stop()
        assert scheduler._thread is None
        assert scheduler._stop_event.is_set()


class TestEnsureSchedulerRunning:
    def setup_method(self):
        stop_scheduler()

    def teardown_method(self):
        stop_scheduler()

    def test_ensure_creates_scheduler(self):
        import zephyr.behavioral_audit.drift_cron_scheduler as mod

        mod._scheduler = None
        scheduler = ensure_scheduler_running()
        assert isinstance(scheduler, DriftCronScheduler)
        stop_scheduler()

    def test_ensure_returns_same_instance(self):
        import zephyr.behavioral_audit.drift_cron_scheduler as mod

        mod._scheduler = None
        s1 = ensure_scheduler_running()
        s2 = ensure_scheduler_running()
        assert s1 is s2
        stop_scheduler()


class TestStopScheduler:
    def test_stop_resets_global(self):
        import zephyr.behavioral_audit.drift_cron_scheduler as mod

        mod._scheduler = None
        ensure_scheduler_running()
        stop_scheduler()
        assert mod._scheduler is None

    def test_stop_when_none_no_error(self):
        import zephyr.behavioral_audit.drift_cron_scheduler as mod

        mod._scheduler = None
        stop_scheduler()
