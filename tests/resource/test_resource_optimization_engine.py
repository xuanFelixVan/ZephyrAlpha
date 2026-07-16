# [A_test] module_id: SRC-TST-1454 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-423 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_resource_optimization_engine
# [INVARIANTS] ResourceOptimizationEngine is singleton; must reset between tests
# [MODIFY-GUARD] resource_optimization_engine.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError on unknown strategy
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

import time

import pytest

from zephyr.shared.lifecycle.daemon_registry import DaemonRegistry
from zephyr.trading.resource_optimization import (
    CircuitBreaker,
    CircuitBreakerState,
    OptimizationStrategy,
    PressureLevel,
    ResourceOptimizationEngine,
)
from zephyr.shared.lifecycle.resource_optimization_models import (
    HealthCheckResult,
    OptimizationRecord,
    OptimizationResult,
    ResourceSnapshot,
)


@pytest.fixture(autouse=True)
def _reset_engine():
    ResourceOptimizationEngine.reset()
    DaemonRegistry.reset()
    yield
    ResourceOptimizationEngine._instance = None
    if ResourceOptimizationEngine._instance is not None:
        ResourceOptimizationEngine._instance.stop_monitor()
    ResourceOptimizationEngine.reset()
    DaemonRegistry.reset()


class TestCircuitBreakerInit:
    def test_defaults(self):
        cb = CircuitBreaker()
        assert cb.state == CircuitBreakerState.CLOSED

    def test_custom_thresholds(self):
        cb = CircuitBreaker(failure_threshold=5, recovery_timeout_s=10.0, half_open_max_calls=3)
        assert cb.state == CircuitBreakerState.CLOSED


class TestCircuitBreakerAllow:
    def test_closed_allows(self):
        cb = CircuitBreaker()
        assert cb.allow() is True

    def test_open_blocks(self):
        cb = CircuitBreaker(failure_threshold=1)
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.allow() is False

    def test_half_open_allows_limited(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout_s=0.0, half_open_max_calls=1)
        cb.record_failure()
        time.sleep(0.01)
        assert cb.allow() is True
        assert cb.state == CircuitBreakerState.HALF_OPEN
        assert cb.allow() is False


class TestCircuitBreakerRecordSuccess:
    def test_resets_from_half_open(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout_s=0.0)
        cb.record_failure()
        time.sleep(0.01)
        cb.allow()
        cb.record_success()
        assert cb.state == CircuitBreakerState.CLOSED

    def test_resets_failure_count(self):
        cb = CircuitBreaker(failure_threshold=3)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        assert cb.state == CircuitBreakerState.CLOSED


class TestCircuitBreakerRecordFailure:
    def test_opens_after_threshold(self):
        cb = CircuitBreaker(failure_threshold=2)
        cb.record_failure()
        assert cb.state == CircuitBreakerState.CLOSED
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN

    def test_half_open_back_to_open(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout_s=60.0)
        cb.record_failure()
        time.sleep(0.01)
        cb.allow()
        cb.record_failure()
        assert cb._state == CircuitBreakerState.OPEN


class TestCircuitBreakerReset:
    def test_reset(self):
        cb = CircuitBreaker(failure_threshold=1)
        cb.record_failure()
        cb.reset()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.allow() is True


class TestResourceOptimizationEngineInit:
    def test_singleton(self):
        e1 = ResourceOptimizationEngine()
        e2 = ResourceOptimizationEngine()
        assert e1 is e2


class TestResourceOptimizationEngineSnapshot:
    def test_snapshot_returns_resource_snapshot(self):
        engine = ResourceOptimizationEngine()
        snap = engine.snapshot()
        assert isinstance(snap, ResourceSnapshot)
        assert snap.timestamp > 0


class TestResourceOptimizationEngineOptimize:
    def test_schedule_adapt(self):
        engine = ResourceOptimizationEngine()
        result = engine.optimize(OptimizationStrategy.SCHEDULE_ADAPT)
        assert isinstance(result, OptimizationResult)
        assert result.success is True
        assert len(result.actions_taken) > 0

    def test_memory_compact(self):
        engine = ResourceOptimizationEngine()
        result = engine.optimize(OptimizationStrategy.MEMORY_COMPACT)
        assert result.success is True
        assert len(result.actions_taken) > 0

    def test_cache_warm_no_files(self):
        engine = ResourceOptimizationEngine()
        result = engine.optimize(OptimizationStrategy.CACHE_WARM)
        assert result.success is True
        assert "no files" in result.actions_taken[0]

    def test_io_batch_no_files(self):
        engine = ResourceOptimizationEngine()
        result = engine.optimize(OptimizationStrategy.IO_BATCH)
        assert result.success is True
        assert "no files" in result.actions_taken[0]

    def test_process_pool_no_active(self):
        engine = ResourceOptimizationEngine()
        result = engine.optimize(OptimizationStrategy.PROCESS_POOL)
        assert result.success is True
        assert "no active" in result.actions_taken[0]

    def test_lazy_init_all_loaded(self):
        engine = ResourceOptimizationEngine()
        result = engine.optimize(OptimizationStrategy.LAZY_INIT)
        assert result.success is True

    def test_streaming_read_no_path(self):
        engine = ResourceOptimizationEngine()
        result = engine.optimize(OptimizationStrategy.STREAMING_READ)
        assert result.success is True
        assert "no path" in result.actions_taken[0]

    def test_optimization_history_recorded(self):
        engine = ResourceOptimizationEngine()
        engine.optimize(OptimizationStrategy.SCHEDULE_ADAPT)
        history = engine.get_optimization_history()
        assert len(history) >= 1
        assert isinstance(history[0], OptimizationRecord)


class TestResourceOptimizationEngineHealthCheck:
    def test_health_check(self):
        engine = ResourceOptimizationEngine()
        hc = engine.health_check()
        assert isinstance(hc, HealthCheckResult)
        assert hc.engine_running is False
        assert hc.monitor_loop_alive is False


class TestResourceOptimizationEnginePressureState:
    def test_get_pressure_state(self):
        engine = ResourceOptimizationEngine()
        state = engine.get_pressure_state()
        assert state.current_level == PressureLevel.NORMAL


class TestResourceOptimizationEngineForcePressure:
    def test_force_pressure(self):
        engine = ResourceOptimizationEngine()
        engine.force_pressure(PressureLevel.CRITICAL, "test")
        state = engine.get_pressure_state()
        assert state.current_level == PressureLevel.CRITICAL


class TestResourceOptimizationEngineDegradationMatrix:
    def test_get_degradation_matrix(self):
        engine = ResourceOptimizationEngine()
        dm = engine.get_degradation_matrix()
        assert "scheduler" in dm.normal
        assert "scheduler" in dm.critical


class TestResourceOptimizationEngineCircuitBreakerStatus:
    def test_empty_initially(self):
        engine = ResourceOptimizationEngine()
        assert engine.get_circuit_breaker_status() == {}

    def test_after_optimize(self):
        engine = ResourceOptimizationEngine()
        engine.optimize(OptimizationStrategy.SCHEDULE_ADAPT)
        status = engine.get_circuit_breaker_status()
        assert "schedule_adapt" in status
        assert status["schedule_adapt"] == CircuitBreakerState.CLOSED


class TestResourceOptimizationEngineMonitor:
    def test_start_stop_monitor(self):
        engine = ResourceOptimizationEngine()
        engine.start_monitor(interval=1.0)
        assert engine._monitor_running is True
        engine.stop_monitor()
        assert engine._monitor_running is False

    def test_start_monitor_idempotent(self):
        engine = ResourceOptimizationEngine()
        engine.start_monitor(interval=1.0)
        engine.start_monitor(interval=1.0)
        assert engine._monitor_running is True
        engine.stop_monitor()


class TestResourceOptimizationEngineDaemonDelegation:
    def test_register_and_start_daemon(self):
        engine = ResourceOptimizationEngine()
        started = []
        engine.register_daemon("d1", lambda: started.append(True), lambda: None, priority=5)
        result = engine.start_daemon("d1")
        assert result is True
        assert len(started) == 1

    def test_stop_daemon(self):
        engine = ResourceOptimizationEngine()
        stopped = []
        engine.register_daemon("d1", lambda: None, lambda: stopped.append(True))
        engine.start_daemon("d1")
        result = engine.stop_daemon("d1")
        assert result is True
        assert len(stopped) == 1


class TestResourceOptimizationEngineCacheAndPool:
    def test_get_cache_stats(self):
        engine = ResourceOptimizationEngine()
        stats = engine.get_cache_stats()
        assert stats.total_entries == 0

    def test_get_process_pool_stats(self):
        engine = ResourceOptimizationEngine()
        stats = engine.get_process_pool_stats()
        assert stats.active_processes == 0

    def test_get_file_cache(self):
        engine = ResourceOptimizationEngine()
        cache = engine.get_file_cache()
        assert cache is not None

    def test_get_process_pool(self):
        engine = ResourceOptimizationEngine()
        pool = engine.get_process_pool()
        assert pool is not None

    def test_get_lazy_loader(self):
        engine = ResourceOptimizationEngine()
        loader = engine.get_lazy_loader()
        assert loader is not None


class TestResourceOptimizationEngineOnPressure:
    def test_register_callback(self):
        engine = ResourceOptimizationEngine()
        engine.on_pressure(lambda lvl, snap: None)
        assert len(engine._pressure_callbacks) == 1
