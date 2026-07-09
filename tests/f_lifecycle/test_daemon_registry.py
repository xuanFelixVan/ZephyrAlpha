# [A_test] module_id: SRC-TST-0693 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-372 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_daemon_registry
# [INVARIANTS] DaemonRegistry uses ClassVar state; must reset between tests
# [MODIFY-GUARD] daemon_registry.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] no raises expected from DaemonRegistry methods
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.shared.lifecycle.daemon_registry import (
    DaemonEntry,
    DaemonRegistry,
    DaemonState,
)


@pytest.fixture(autouse=True)
def _reset_registry():
    DaemonRegistry.reset()
    yield
    DaemonRegistry.reset()


class TestDaemonEntry:
    def test_defaults(self):
        entry = DaemonEntry(name="d1", start_fn=lambda: None, stop_fn=lambda: None)
        assert entry.name == "d1"
        assert entry.state == DaemonState.STOPPED
        assert entry.priority == 0
        assert entry.error_count == 0
        assert entry.last_error == ""
        assert entry.started_at == 0.0

    def test_custom_values(self):
        entry = DaemonEntry(
            name="d2",
            start_fn=lambda: None,
            stop_fn=lambda: None,
            priority=5,
            state=DaemonState.RUNNING,
            error_count=2,
            last_error="boom",
        )
        assert entry.priority == 5
        assert entry.state == DaemonState.RUNNING
        assert entry.error_count == 2
        assert entry.last_error == "boom"


class TestDaemonState:
    def test_values(self):
        assert DaemonState.STOPPED == "STOPPED"
        assert DaemonState.STARTING == "STARTING"
        assert DaemonState.RUNNING == "RUNNING"
        assert DaemonState.STOPPING == "STOPPING"
        assert DaemonState.FAILED == "FAILED"


class TestDaemonRegistryRegister:
    def test_register_new(self):
        DaemonRegistry.register("d1", lambda: None, lambda: None, priority=3)
        assert DaemonRegistry.is_running("d1") is False
        status = DaemonRegistry.status()
        assert "d1" in status
        assert status["d1"]["priority"] == 3

    def test_register_duplicate_skipped(self):
        DaemonRegistry.register("d1", lambda: None, lambda: None)
        DaemonRegistry.register("d1", lambda: None, lambda: None, priority=10)
        status = DaemonRegistry.status()
        assert status["d1"]["priority"] == 0

    def test_register_empty_name(self):
        DaemonRegistry.register("", lambda: None, lambda: None)
        assert "" in DaemonRegistry.status()


class TestDaemonRegistryStartStop:
    def test_start_success(self):
        started = []
        DaemonRegistry.register("d1", lambda: started.append(True), lambda: None)
        result = DaemonRegistry.start("d1")
        assert result is True
        assert DaemonRegistry.is_running("d1") is True
        assert len(started) == 1

    def test_start_not_registered(self):
        result = DaemonRegistry.start("nonexistent")
        assert result is False

    def test_start_already_running(self):
        DaemonRegistry.register("d1", lambda: None, lambda: None)
        DaemonRegistry.start("d1")
        result = DaemonRegistry.start("d1")
        assert result is True

    def test_start_failure(self):
        def bad_start():
            raise RuntimeError("fail")

        DaemonRegistry.register("d1", bad_start, lambda: None)
        result = DaemonRegistry.start("d1")
        assert result is False
        status = DaemonRegistry.status()
        assert status["d1"]["state"] == "FAILED"
        assert status["d1"]["error_count"] == 1

    def test_stop_success(self):
        stopped = []
        DaemonRegistry.register("d1", lambda: None, lambda: stopped.append(True))
        DaemonRegistry.start("d1")
        result = DaemonRegistry.stop("d1")
        assert result is True
        assert DaemonRegistry.is_running("d1") is False
        assert len(stopped) == 1

    def test_stop_not_registered(self):
        result = DaemonRegistry.stop("nonexistent")
        assert result is False

    def test_stop_not_running(self):
        DaemonRegistry.register("d1", lambda: None, lambda: None)
        result = DaemonRegistry.stop("d1")
        assert result is True

    def test_stop_failure(self):
        def bad_stop():
            raise RuntimeError("stop-fail")

        DaemonRegistry.register("d1", lambda: None, bad_stop)
        DaemonRegistry.start("d1")
        result = DaemonRegistry.stop("d1")
        assert result is False
        status = DaemonRegistry.status()
        assert status["d1"]["state"] == "FAILED"


class TestDaemonRegistryStartAllStopAll:
    def test_start_all(self):
        DaemonRegistry.register("d1", lambda: None, lambda: None)
        DaemonRegistry.register("d2", lambda: None, lambda: None)
        results = DaemonRegistry.start_all()
        assert results["d1"] is True
        assert results["d2"] is True

    def test_stop_all(self):
        DaemonRegistry.register("d1", lambda: None, lambda: None)
        DaemonRegistry.register("d2", lambda: None, lambda: None)
        DaemonRegistry.start_all()
        results = DaemonRegistry.stop_all()
        assert results["d1"] is True
        assert results["d2"] is True


class TestDaemonRegistryStopLowPriority:
    def test_stops_low_priority(self):
        DaemonRegistry.register("low", lambda: None, lambda: None, priority=1)
        DaemonRegistry.register("high", lambda: None, lambda: None, priority=10)
        DaemonRegistry.start_all()
        stopped = DaemonRegistry.stop_low_priority(min_priority=5)
        assert "low" in stopped
        assert "high" not in stopped

    def test_no_candidates(self):
        DaemonRegistry.register("high", lambda: None, lambda: None, priority=10)
        DaemonRegistry.start("high")
        stopped = DaemonRegistry.stop_low_priority(min_priority=5)
        assert stopped == []


class TestDaemonRegistryStatus:
    def test_status_empty(self):
        assert DaemonRegistry.status() == {}

    def test_status_with_entries(self):
        DaemonRegistry.register("d1", lambda: None, lambda: None)
        status = DaemonRegistry.status()
        assert "d1" in status
        assert status["d1"]["state"] == "STOPPED"
        assert status["d1"]["uptime_s"] == 0

    def test_uptime_when_running(self):
        DaemonRegistry.register("d1", lambda: None, lambda: None)
        DaemonRegistry.start("d1")
        status = DaemonRegistry.status()
        assert status["d1"]["uptime_s"] >= 0
        assert status["d1"]["state"] == "RUNNING"


class TestDaemonRegistryIsRunning:
    def test_not_registered(self):
        assert DaemonRegistry.is_running("nope") is False

    def test_stopped(self):
        DaemonRegistry.register("d1", lambda: None, lambda: None)
        assert DaemonRegistry.is_running("d1") is False

    def test_running(self):
        DaemonRegistry.register("d1", lambda: None, lambda: None)
        DaemonRegistry.start("d1")
        assert DaemonRegistry.is_running("d1") is True


class TestDaemonRegistryReset:
    def test_reset_clears_entries(self):
        DaemonRegistry.register("d1", lambda: None, lambda: None)
        DaemonRegistry.reset()
        assert DaemonRegistry.status() == {}
