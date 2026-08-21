# [A_test] module_id: MOD-GOV_resource_optimization | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_resource_optimization
# [INVARIANTS] ResourceOptimizationEngine是单例;每个测试前必须reset
# [MODIFY-GUARD] src/zephyr/runtime/resource_optimization.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] snapshot返回ResourceSnapshot;optimize返回OptimizationResult;CircuitBreaker状态机正确
# [TESTS] tests/test_resource_optimization.py
# [TTL] task_bound

from __future__ import annotations

import time

import pytest

from zephyr.shared.lifecycle.resource_optimization_models import (
    CircuitBreakerState,
    OptimizationStrategy,
    PressureLevel,
)
from zephyr.trading.resource_optimization import (
    CircuitBreaker,
    ResourceOptimizationEngine,
)


@pytest.fixture(autouse=True)
def _reset_singleton():
    ResourceOptimizationEngine.reset()
    yield
    ResourceOptimizationEngine.reset()


class TestCircuitBreaker:
    def test_initial_state_closed(self):
        cb = CircuitBreaker()
        assert cb.state == CircuitBreakerState.CLOSED

    def test_allow_when_closed(self):
        cb = CircuitBreaker()
        assert cb.allow() is True

    def test_opens_after_threshold_failures(self):
        cb = CircuitBreaker(failure_threshold=3)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitBreakerState.CLOSED
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN

    def test_open_blocks_requests(self):
        cb = CircuitBreaker(failure_threshold=1)
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.allow() is False

    def test_half_open_after_recovery_timeout(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout_s=0.01)
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        time.sleep(0.02)
        # 5.91.3 契约：state getter 仅返回当前状态不做转换，OPEN→HALF_OPEN
        # 转换仅在 allow() 内触发（见 CircuitBreaker._try_recover 注释）
        cb.allow()
        assert cb.state == CircuitBreakerState.HALF_OPEN

    def test_half_open_allows_limited_calls(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout_s=0.01, half_open_max_calls=1)
        cb.record_failure()
        time.sleep(0.02)
        assert cb.allow() is True
        assert cb.allow() is False

    def test_success_closes_from_half_open(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout_s=0.01)
        cb.record_failure()
        time.sleep(0.02)
        cb.allow()
        cb.record_success()
        assert cb.state == CircuitBreakerState.CLOSED

    def test_failure_reopens_from_half_open(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout_s=0.01)
        cb.record_failure()
        time.sleep(0.02)
        cb.allow()
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN

    def test_reset(self):
        cb = CircuitBreaker(failure_threshold=1)
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        cb.reset()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.allow() is True


class TestResourceOptimizationEngineInit:
    def test_singleton(self):
        e1 = ResourceOptimizationEngine()
        e2 = ResourceOptimizationEngine()
        assert e1 is e2

    def test_reset_creates_new_instance(self):
        e1 = ResourceOptimizationEngine()
        ResourceOptimizationEngine.reset()
        e2 = ResourceOptimizationEngine()
        assert e1 is not e2


class TestSnapshot:
    def test_snapshot_returns_resource_snapshot(self):
        engine = ResourceOptimizationEngine()
        snap = engine.snapshot()
        assert snap.timestamp > 0
        assert snap.memory_percent >= 0
        assert snap.cpu_percent >= 0
        assert snap.process_count >= 0

    def test_snapshot_classifies_pressure(self):
        engine = ResourceOptimizationEngine()
        snap = engine.snapshot()
        assert snap.pressure in (
            PressureLevel.NORMAL,
            PressureLevel.WARNING,
            PressureLevel.CRITICAL,
            PressureLevel.EMERGENCY,
        )


class TestOptimize:
    def test_memory_compact_succeeds(self):
        engine = ResourceOptimizationEngine()
        result = engine.optimize(OptimizationStrategy.MEMORY_COMPACT)
        assert result.success is True
        assert result.strategy == OptimizationStrategy.MEMORY_COMPACT
        assert len(result.actions_taken) > 0

    def test_schedule_adapt_normal(self):
        engine = ResourceOptimizationEngine()
        result = engine.optimize(OptimizationStrategy.SCHEDULE_ADAPT)
        assert result.success is True
        assert result.strategy == OptimizationStrategy.SCHEDULE_ADAPT

    def test_cache_warm_no_context(self):
        engine = ResourceOptimizationEngine()
        result = engine.optimize(OptimizationStrategy.CACHE_WARM)
        assert result.success is True
        assert "no files" in result.actions_taken[0]

    def test_io_batch_no_context(self):
        engine = ResourceOptimizationEngine()
        result = engine.optimize(OptimizationStrategy.IO_BATCH)
        assert result.success is True
        assert "no files" in result.actions_taken[0]

    def test_streaming_read_no_context(self):
        engine = ResourceOptimizationEngine()
        result = engine.optimize(OptimizationStrategy.STREAMING_READ)
        assert result.success is True
        assert "no path" in result.actions_taken[0]

    def test_lazy_init(self):
        engine = ResourceOptimizationEngine()
        result = engine.optimize(OptimizationStrategy.LAZY_INIT)
        assert result.success is True

    def test_process_pool(self):
        engine = ResourceOptimizationEngine()
        result = engine.optimize(OptimizationStrategy.PROCESS_POOL)
        assert result.success is True


class TestHealthCheck:
    def test_health_check_returns_result(self):
        engine = ResourceOptimizationEngine()
        hc = engine.health_check()
        assert hc.engine_running is False
        assert hc.monitor_loop_alive is False
        assert hc.pressure_level == PressureLevel.NORMAL


class TestForcePressure:
    def test_force_pressure_changes_level(self):
        engine = ResourceOptimizationEngine()
        engine.force_pressure(PressureLevel.CRITICAL, "test")
        ps = engine.get_pressure_state()
        assert ps.current_level == PressureLevel.CRITICAL


class TestGetCircuitBreakerStatus:
    def test_empty_initially(self):
        engine = ResourceOptimizationEngine()
        assert engine.get_circuit_breaker_status() == {}

    def test_after_optimize(self):
        engine = ResourceOptimizationEngine()
        engine.optimize(OptimizationStrategy.MEMORY_COMPACT)
        status = engine.get_circuit_breaker_status()
        assert "memory_compact" in status


class TestOptimizationHistory:
    def test_history_records(self):
        engine = ResourceOptimizationEngine()
        engine.optimize(OptimizationStrategy.MEMORY_COMPACT)
        history = engine.get_optimization_history()
        assert len(history) >= 1
        assert history[-1].strategy == OptimizationStrategy.MEMORY_COMPACT


class TestStartStopMonitor:
    def test_start_and_stop(self):
        engine = ResourceOptimizationEngine()
        engine.start_monitor(interval=1.0)
        assert engine.monitor_running is True
        engine.stop_monitor()
        assert engine.monitor_running is False

    def test_start_idempotent(self):
        engine = ResourceOptimizationEngine()
        engine.start_monitor(interval=1.0)
        engine.start_monitor(interval=1.0)
        assert engine.monitor_running is True
        engine.stop_monitor()


class TestOnPressure:
    def test_callback_registered(self):
        engine = ResourceOptimizationEngine()
        called = []
        engine.on_pressure(lambda level, snap: called.append(level))
        assert len(engine.pressure_callbacks) == 1
