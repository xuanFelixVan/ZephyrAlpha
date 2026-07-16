# [A_test] module_id: SRC-TST-1929 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-548 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.resource_optimization.test_engine
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
test_engine.py - ResourceOptimizationEngine unit tests
======================================================

TASK-INF-0139 Phase 1 verification.

Covers:
  - ResourceSnapshot data model (9 metrics + pressure)
  - PressureLevel classification (4 levels + boundary values)
  - PressureStateMachine (hysteresis, cooldown, anti-oscillation)
  - CircuitBreaker (CLOSED/OPEN/HALF_OPEN transitions)
  - Defensive strategy engine (EMERGENCY/CRITICAL)
  - Optimization strategy engine (SCHEDULE_ADAPT, MEMORY_COMPACT)
  - optimize() unified dispatch with circuit breaker
  - health_check()
  - Singleton pattern
"""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

from zephyr.trading.resource_optimization import (
    CacheStats,
    CircuitBreaker,
    CircuitBreakerState,
    DegradationMatrix,
    HealthCheckResult,
    OptimizationStrategy,
    PressureLevel,
    PressureState,
    ProcessPoolStats,
    ResourceOptimizationEngine,
    ResourceSnapshot,
    _HysteresisConfig,
    _PressureStateMachine,
)


class TestResourceSnapshot:
    def test_defaults(self):
        snap = ResourceSnapshot()
        assert snap.cpu_percent == 0.0
        assert snap.memory_percent == 0.0
        assert snap.process_count == 0
        assert snap.thread_count == 0
        assert snap.disk_io_read_mb_s == 0.0
        assert snap.disk_io_write_mb_s == 0.0
        assert snap.disk_free_gb == 0.0
        assert snap.pressure == PressureLevel.NORMAL

    def test_clamp_percent(self):
        snap = ResourceSnapshot(cpu_percent=150.0, memory_percent=-10.0)
        assert snap.cpu_percent == 100.0
        assert snap.memory_percent == 0.0

    def test_all_fields_present(self):
        snap = ResourceSnapshot(
            cpu_percent=50.0,
            memory_percent=60.0,
            memory_used_gb=8.0,
            memory_total_gb=16.0,
            process_count=30,
            thread_count=200,
            disk_io_read_mb_s=10.0,
            disk_io_write_mb_s=5.0,
            disk_free_gb=100.0,
            pressure=PressureLevel.WARNING,
        )
        assert snap.memory_used_gb == 8.0
        assert snap.disk_free_gb == 100.0


class TestPressureClassification:
    def setup_method(self):
        ResourceOptimizationEngine.reset()
        self.engine = ResourceOptimizationEngine()

    def teardown_method(self):
        ResourceOptimizationEngine.reset()

    def test_normal(self):
        snap = ResourceSnapshot(memory_percent=50.0, cpu_percent=50.0, process_count=20)
        assert self.engine._classify_pressure(snap) == PressureLevel.NORMAL

    def test_warning_memory(self):
        snap = ResourceSnapshot(memory_percent=76.0, cpu_percent=50.0, process_count=20)
        assert self.engine._classify_pressure(snap) == PressureLevel.WARNING

    def test_warning_cpu(self):
        snap = ResourceSnapshot(memory_percent=50.0, cpu_percent=81.0, process_count=20)
        assert self.engine._classify_pressure(snap) == PressureLevel.WARNING

    def test_warning_process(self):
        snap = ResourceSnapshot(memory_percent=50.0, cpu_percent=50.0, process_count=55)
        assert self.engine._classify_pressure(snap) == PressureLevel.WARNING

    def test_critical_memory(self):
        snap = ResourceSnapshot(memory_percent=86.0, cpu_percent=50.0, process_count=20)
        assert self.engine._classify_pressure(snap) == PressureLevel.CRITICAL

    def test_critical_cpu(self):
        snap = ResourceSnapshot(memory_percent=50.0, cpu_percent=91.0, process_count=20)
        assert self.engine._classify_pressure(snap) == PressureLevel.CRITICAL

    def test_critical_process(self):
        snap = ResourceSnapshot(memory_percent=50.0, cpu_percent=50.0, process_count=110)
        assert self.engine._classify_pressure(snap) == PressureLevel.CRITICAL

    def test_emergency_memory(self):
        snap = ResourceSnapshot(memory_percent=96.0, cpu_percent=50.0, process_count=20)
        assert self.engine._classify_pressure(snap) == PressureLevel.EMERGENCY

    def test_emergency_cpu(self):
        snap = ResourceSnapshot(memory_percent=50.0, cpu_percent=99.0, process_count=20)
        assert self.engine._classify_pressure(snap) == PressureLevel.EMERGENCY

    def test_emergency_process(self):
        snap = ResourceSnapshot(memory_percent=50.0, cpu_percent=50.0, process_count=260)
        assert self.engine._classify_pressure(snap) == PressureLevel.EMERGENCY

    def test_boundary_warning(self):
        snap = ResourceSnapshot(memory_percent=75.0, cpu_percent=50.0, process_count=20)
        assert self.engine._classify_pressure(snap) == PressureLevel.WARNING

    def test_boundary_critical(self):
        snap = ResourceSnapshot(memory_percent=85.0, cpu_percent=50.0, process_count=20)
        assert self.engine._classify_pressure(snap) == PressureLevel.CRITICAL

    def test_boundary_emergency(self):
        snap = ResourceSnapshot(memory_percent=95.0, cpu_percent=50.0, process_count=20)
        assert self.engine._classify_pressure(snap) == PressureLevel.EMERGENCY


class TestPressureStateMachine:
    def test_initial_state(self):
        sm = _PressureStateMachine()
        assert sm.current == PressureLevel.NORMAL
        state = sm.state
        assert state.current_level == PressureLevel.NORMAL
        assert state.previous_level is None
        assert state.transition_count == 0

    def test_escalation_needs_confirmation(self):
        sm = _PressureStateMachine(_HysteresisConfig(confirmation_count=2))
        result = sm.transition(PressureLevel.WARNING)
        assert result == PressureLevel.NORMAL
        result = sm.transition(PressureLevel.WARNING)
        assert result == PressureLevel.WARNING

    def test_escalation_different_level_resets_counter(self):
        sm = _PressureStateMachine(_HysteresisConfig(confirmation_count=2))
        sm.transition(PressureLevel.WARNING)
        sm.transition(PressureLevel.CRITICAL)
        assert sm.current == PressureLevel.NORMAL

    def test_same_level_no_transition(self):
        sm = _PressureStateMachine(_HysteresisConfig(confirmation_count=2))
        sm.transition(PressureLevel.WARNING)
        sm.transition(PressureLevel.WARNING)
        assert sm.current == PressureLevel.WARNING
        sm.transition(PressureLevel.WARNING)
        assert sm.current == PressureLevel.WARNING
        assert sm.state.transition_count == 1

    def test_deescalation_cooldown(self):
        sm = _PressureStateMachine(_HysteresisConfig(confirmation_count=1, cooldown_seconds=10.0))
        sm.transition(PressureLevel.WARNING)
        assert sm.current == PressureLevel.WARNING
        result = sm.transition(PressureLevel.NORMAL)
        assert result == PressureLevel.WARNING

    def test_deescalation_after_cooldown(self):
        sm = _PressureStateMachine(_HysteresisConfig(confirmation_count=1, cooldown_seconds=0.0))
        sm.transition(PressureLevel.WARNING)
        assert sm.current == PressureLevel.WARNING
        result = sm.transition(PressureLevel.NORMAL)
        assert result == PressureLevel.NORMAL

    def test_anti_oscillation_increases_confirmation(self):
        config = _HysteresisConfig(
            confirmation_count=1,
            cooldown_seconds=0.0,
            oscillation_threshold_per_hour=2,
        )
        sm = _PressureStateMachine(config)
        sm.transition(PressureLevel.WARNING)
        sm.transition(PressureLevel.NORMAL)
        sm.transition(PressureLevel.WARNING)
        sm.transition(PressureLevel.NORMAL)
        assert sm.current == PressureLevel.NORMAL
        result = sm.transition(PressureLevel.WARNING)
        assert result == PressureLevel.NORMAL
        result = sm.transition(PressureLevel.WARNING)
        assert result == PressureLevel.WARNING


class TestCircuitBreaker:
    def test_initial_closed(self):
        cb = CircuitBreaker()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.allow() is True

    def test_opens_after_failures(self):
        cb = CircuitBreaker(failure_threshold=3)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitBreakerState.CLOSED
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.allow() is False

    def test_half_open_after_timeout(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout_s=0.05)
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        time.sleep(0.1)
        assert cb.state == CircuitBreakerState.HALF_OPEN
        assert cb.allow() is True

    def test_half_open_success_closes(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout_s=0.05)
        cb.record_failure()
        time.sleep(0.1)
        assert cb.state == CircuitBreakerState.HALF_OPEN
        cb.record_success()
        assert cb.state == CircuitBreakerState.CLOSED

    def test_half_open_failure_reopens(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout_s=0.05)
        cb.record_failure()
        time.sleep(0.1)
        assert cb.state == CircuitBreakerState.HALF_OPEN
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN

    def test_half_open_max_calls(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout_s=0.05, half_open_max_calls=1)
        cb.record_failure()
        time.sleep(0.1)
        assert cb.state == CircuitBreakerState.HALF_OPEN
        assert cb.allow() is True
        assert cb.allow() is False

    def test_reset(self):
        cb = CircuitBreaker(failure_threshold=1)
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        cb.reset()
        assert cb.state == CircuitBreakerState.CLOSED


class TestResourceOptimizationEngine:
    def setup_method(self):
        ResourceOptimizationEngine.reset()

    def teardown_method(self):
        ResourceOptimizationEngine.reset()

    def test_singleton(self):
        e1 = ResourceOptimizationEngine()
        e2 = ResourceOptimizationEngine()
        assert e1 is e2

    def test_reset_creates_new_instance(self):
        e1 = ResourceOptimizationEngine()
        ResourceOptimizationEngine.reset()
        e2 = ResourceOptimizationEngine()
        assert e1 is not e2

    @patch("zephyr.infrastructure.shared_services.lifecycle.resource_optimization_engine.psutil", create=True)
    def test_snapshot_with_psutil(self, mock_psutil):
        mock_mem = MagicMock()
        mock_mem.percent = 65.0
        mock_mem.used = 10 * 1024**3
        mock_mem.total = 16 * 1024**3
        mock_psutil.virtual_memory.return_value = mock_mem
        mock_psutil.cpu_percent.return_value = 45.0
        mock_psutil.pids.return_value = list(range(30))
        mock_psutil.process_iter.return_value = []
        mock_psutil.Error = Exception

        import sys

        sys.modules["psutil"] = mock_psutil

        try:
            engine = ResourceOptimizationEngine()
            snap = engine.snapshot()
            assert snap.memory_percent == 65.0
            assert snap.cpu_percent == 45.0
            assert snap.process_count == 30
        finally:
            del sys.modules["psutil"]

    def test_snapshot_without_psutil(self):
        engine = ResourceOptimizationEngine()
        snap = engine.snapshot()
        assert isinstance(snap, ResourceSnapshot)
        assert snap.memory_percent >= 0.0

    def test_optimize_schedule_adapt(self):
        engine = ResourceOptimizationEngine()
        result = engine.optimize(OptimizationStrategy.SCHEDULE_ADAPT)
        assert result.success is True
        assert len(result.actions_taken) > 0

    def test_optimize_memory_compact(self):
        engine = ResourceOptimizationEngine()
        result = engine.optimize(OptimizationStrategy.MEMORY_COMPACT)
        assert result.success is True
        assert "memory_compact" in result.actions_taken[0]

    def test_optimize_io_strategies(self):
        engine = ResourceOptimizationEngine()
        result = engine.optimize(OptimizationStrategy.CACHE_WARM)
        assert result.success is True
        result = engine.optimize(OptimizationStrategy.IO_BATCH)
        assert result.success is True
        result = engine.optimize(OptimizationStrategy.STREAMING_READ)
        assert result.success is True

    def test_optimize_circuit_breaker_blocks(self):
        engine = ResourceOptimizationEngine()
        cb = engine._circuit_breakers["cache_warm"] = CircuitBreaker(failure_threshold=1)
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        result = engine.optimize(OptimizationStrategy.CACHE_WARM)
        assert result.success is False
        assert "circuit breaker OPEN" in (result.error_message or "")

    def test_optimization_history(self):
        engine = ResourceOptimizationEngine()
        engine.optimize(OptimizationStrategy.SCHEDULE_ADAPT)
        engine.optimize(OptimizationStrategy.MEMORY_COMPACT)
        history = engine.get_optimization_history()
        assert len(history) == 2

    def test_health_check(self):
        engine = ResourceOptimizationEngine()
        health = engine.health_check()
        assert isinstance(health, HealthCheckResult)
        assert health.engine_running is False
        assert health.monitor_loop_alive is False
        assert health.pressure_level == PressureLevel.NORMAL

    def test_get_pressure_state(self):
        engine = ResourceOptimizationEngine()
        state = engine.get_pressure_state()
        assert isinstance(state, PressureState)
        assert state.current_level == PressureLevel.NORMAL

    def test_on_pressure_callback(self):
        engine = ResourceOptimizationEngine()
        received = []
        engine.on_pressure(lambda level, snap: received.append((level, snap)))
        engine._pressure_callbacks[0](PressureLevel.WARNING, ResourceSnapshot())
        assert len(received) == 1
        assert received[0][0] == PressureLevel.WARNING

    def test_degradation_matrix(self):
        engine = ResourceOptimizationEngine()
        matrix = engine.get_degradation_matrix()
        assert isinstance(matrix, DegradationMatrix)
        assert "scheduler" in matrix.emergency
        assert matrix.emergency["scheduler"] == "paused"

    def test_get_cache_stats(self):
        engine = ResourceOptimizationEngine()
        stats = engine.get_cache_stats()
        assert isinstance(stats, CacheStats)

    def test_get_process_pool_stats(self):
        engine = ResourceOptimizationEngine()
        stats = engine.get_process_pool_stats()
        assert isinstance(stats, ProcessPoolStats)


class TestMonitorLoop:
    def setup_method(self):
        ResourceOptimizationEngine.reset()

    def teardown_method(self):
        ResourceOptimizationEngine.reset()

    def test_start_stop_monitor(self):
        engine = ResourceOptimizationEngine()
        engine.start_monitor(interval=1.0)
        time.sleep(0.5)
        health = engine.health_check()
        assert health.engine_running is True
        assert health.monitor_loop_alive is True
        engine.stop_monitor()
        time.sleep(1.5)
        health = engine.health_check()
        assert health.engine_running is False

    def test_monitor_updates_snapshot(self):
        engine = ResourceOptimizationEngine()
        engine.start_monitor(interval=0.5)
        time.sleep(1.0)
        health = engine.health_check()
        assert health.last_snapshot_age_s < 5.0
        engine.stop_monitor()
        time.sleep(1.0)


class TestDefensiveStrategy:
    def setup_method(self):
        ResourceOptimizationEngine.reset()

    def teardown_method(self):
        ResourceOptimizationEngine.reset()

    @patch.object(ResourceOptimizationEngine, "_execute_defensive")
    def test_emergency_triggers_defensive(self, mock_defensive):
        mock_defensive.return_value = ["stop_low_priority(5): stopped 2"]
        engine = ResourceOptimizationEngine()
        engine.force_pressure(PressureLevel.EMERGENCY, "test")
        assert engine.get_pressure_state().current_level == PressureLevel.EMERGENCY
