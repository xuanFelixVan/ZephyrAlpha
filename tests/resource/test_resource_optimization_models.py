# [A_test] module_id: MOD-GOV_resource_optimization_models | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-424 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_resource_optimization_models
# [INVARIANTS] Pydantic models validate on construction
# [MODIFY-GUARD] resource_optimization_models.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] Pydantic ValidationError on invalid input
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from zephyr.shared.lifecycle.resource_optimization_models import (
    CacheStats,
    CircuitBreakerState,
    DefensiveStrategy,
    DegradationMatrix,
    HealthCheckResult,
    OptimizationRecord,
    OptimizationResult,
    OptimizationStrategy,
    PressureLevel,
    PressureState,
    ProcessPoolStats,
    ResourceSnapshot,
)


class TestPressureLevel:
    def test_values(self):
        assert PressureLevel.NORMAL == "normal"
        assert PressureLevel.WARNING == "warning"
        assert PressureLevel.CRITICAL == "critical"
        assert PressureLevel.EMERGENCY == "emergency"


class TestOptimizationStrategy:
    def test_values(self):
        expected = [
            "cache_warm",
            "io_batch",
            "process_pool",
            "lazy_init",
            "streaming_read",
            "schedule_adapt",
            "memory_compact",
        ]
        actual = [s.value for s in OptimizationStrategy]
        assert actual == expected


class TestDefensiveStrategy:
    def test_values(self):
        assert DefensiveStrategy.STOP_LOW_PRIORITY == "stop_low_priority"
        assert DefensiveStrategy.RELEASE_MEMORY == "release_memory"
        assert DefensiveStrategy.REDUCE_FREQUENCY == "reduce_frequency"
        assert DefensiveStrategy.EMERGENCY_GC == "emergency_gc"


class TestCircuitBreakerState:
    def test_values(self):
        assert CircuitBreakerState.CLOSED == "closed"
        assert CircuitBreakerState.OPEN == "open"
        assert CircuitBreakerState.HALF_OPEN == "half_open"


class TestResourceSnapshot:
    def test_defaults(self):
        snap = ResourceSnapshot()
        assert snap.cpu_percent == 0.0
        assert snap.memory_percent == 0.0
        assert snap.memory_used_gb == 0.0
        assert snap.memory_total_gb == 0.0
        assert snap.process_count == 0
        assert snap.thread_count == 0
        assert snap.pressure == PressureLevel.NORMAL
        assert snap.disk_io_read_mb_s == 0.0
        assert snap.disk_io_write_mb_s == 0.0
        assert snap.disk_free_gb == 0.0

    def test_custom_values(self):
        snap = ResourceSnapshot(
            cpu_percent=50.0,
            memory_percent=75.0,
            memory_used_gb=8.0,
            memory_total_gb=16.0,
            process_count=42,
            thread_count=100,
            pressure=PressureLevel.WARNING,
        )
        assert snap.cpu_percent == 50.0
        assert snap.memory_percent == 75.0
        assert snap.process_count == 42
        assert snap.pressure == PressureLevel.WARNING

    def test_clamp_percent_above_100(self):
        snap = ResourceSnapshot(cpu_percent=150.0, memory_percent=200.0)
        assert snap.cpu_percent == 100.0
        assert snap.memory_percent == 100.0

    def test_clamp_percent_below_0(self):
        snap = ResourceSnapshot(cpu_percent=-10.0, memory_percent=-5.0)
        assert snap.cpu_percent == 0.0
        assert snap.memory_percent == 0.0

    def test_negative_memory_rejected(self):
        with pytest.raises(ValidationError):
            ResourceSnapshot(memory_used_gb=-1.0)

    def test_negative_process_count_rejected(self):
        with pytest.raises(ValidationError):
            ResourceSnapshot(process_count=-1)

    def test_timestamp_auto_set(self):
        snap = ResourceSnapshot()
        assert snap.timestamp > 0


class TestOptimizationRecord:
    def test_defaults(self):
        rec = OptimizationRecord(
            trigger=PressureLevel.WARNING,
            strategy=OptimizationStrategy.MEMORY_COMPACT,
        )
        assert rec.trigger == PressureLevel.WARNING
        assert rec.strategy == OptimizationStrategy.MEMORY_COMPACT
        assert rec.actions_taken == []
        assert rec.quality_preserved is True
        assert rec.success is True
        assert rec.duration_ms == 0

    def test_custom(self):
        rec = OptimizationRecord(
            trigger=PressureLevel.EMERGENCY,
            strategy=OptimizationStrategy.SCHEDULE_ADAPT,
            actions_taken=["action1"],
            memory_before_gb=10.0,
            memory_after_gb=8.0,
            process_count_before=100,
            process_count_after=80,
            quality_preserved=False,
            duration_ms=500,
            success=True,
        )
        assert rec.memory_before_gb == 10.0
        assert rec.memory_after_gb == 8.0
        assert rec.quality_preserved is False

    def test_negative_duration_rejected(self):
        with pytest.raises(ValidationError):
            OptimizationRecord(
                trigger=PressureLevel.NORMAL,
                strategy=OptimizationStrategy.MEMORY_COMPACT,
                duration_ms=-1,
            )


class TestOptimizationResult:
    def test_minimal(self):
        snap = ResourceSnapshot()
        result = OptimizationResult(
            strategy=OptimizationStrategy.CACHE_WARM,
            success=True,
            snapshot_before=snap,
        )
        assert result.success is True
        assert result.actions_taken == []
        assert result.snapshot_after is None
        assert result.quality_preserved is True
        assert result.error_message is None

    def test_with_error(self):
        snap = ResourceSnapshot()
        result = OptimizationResult(
            strategy=OptimizationStrategy.IO_BATCH,
            success=False,
            snapshot_before=snap,
            error_message="something broke",
        )
        assert result.success is False
        assert result.error_message == "something broke"


class TestCacheStats:
    def test_defaults(self):
        stats = CacheStats()
        assert stats.total_entries == 0
        assert stats.hit_count == 0
        assert stats.miss_count == 0
        assert stats.hit_rate == 0.0
        assert stats.memory_usage_mb == 0.0
        assert stats.evictions == 0

    def test_custom(self):
        stats = CacheStats(
            total_entries=10,
            hit_count=8,
            miss_count=2,
            hit_rate=0.8,
            memory_usage_mb=5.5,
            evictions=1,
        )
        assert stats.hit_rate == 0.8

    def test_hit_rate_above_1_rejected(self):
        with pytest.raises(ValidationError):
            CacheStats(hit_rate=1.5)

    def test_negative_entries_rejected(self):
        with pytest.raises(ValidationError):
            CacheStats(total_entries=-1)


class TestProcessPoolStats:
    def test_defaults(self):
        stats = ProcessPoolStats()
        assert stats.active_processes == 0
        assert stats.max_processes == 30
        assert stats.reuse_count == 0
        assert stats.zombie_count == 0

    def test_custom(self):
        stats = ProcessPoolStats(
            active_processes=5,
            max_processes=50,
            reuse_count=100,
            zombie_count=2,
        )
        assert stats.active_processes == 5
        assert stats.max_processes == 50

    def test_zero_max_processes_rejected(self):
        with pytest.raises(ValidationError):
            ProcessPoolStats(max_processes=0)

    def test_negative_active_rejected(self):
        with pytest.raises(ValidationError):
            ProcessPoolStats(active_processes=-1)


class TestPressureState:
    def test_defaults(self):
        state = PressureState()
        assert state.current_level == PressureLevel.NORMAL
        assert state.previous_level is None
        assert state.transition_count == 0
        assert state.cooldown_remaining_s == 0.0

    def test_custom(self):
        now = datetime.now(UTC)
        state = PressureState(
            current_level=PressureLevel.CRITICAL,
            previous_level=PressureLevel.WARNING,
            entered_at=now,
            transition_count=5,
            cooldown_remaining_s=30.0,
        )
        assert state.current_level == PressureLevel.CRITICAL
        assert state.previous_level == PressureLevel.WARNING
        assert state.transition_count == 5

    def test_negative_transition_count_rejected(self):
        with pytest.raises(ValidationError):
            PressureState(transition_count=-1)


class TestHealthCheckResult:
    def test_required_fields(self):
        hc = HealthCheckResult(engine_running=True, monitor_loop_alive=True)
        assert hc.engine_running is True
        assert hc.monitor_loop_alive is True
        assert hc.last_snapshot_age_s == 0.0
        assert hc.pressure_level == PressureLevel.NORMAL
        assert hc.daemon_count == 0
        assert hc.cache_healthy is True
        assert hc.process_pool_healthy is True

    def test_custom(self):
        hc = HealthCheckResult(
            engine_running=False,
            monitor_loop_alive=False,
            last_snapshot_age_s=45.0,
            pressure_level=PressureLevel.WARNING,
            daemon_count=3,
            cache_healthy=False,
        )
        assert hc.last_snapshot_age_s == 45.0
        assert hc.daemon_count == 3
        assert hc.cache_healthy is False

    def test_negative_daemon_count_rejected(self):
        with pytest.raises(ValidationError):
            HealthCheckResult(engine_running=True, monitor_loop_alive=True, daemon_count=-1)


class TestDegradationMatrix:
    def test_defaults(self):
        dm = DegradationMatrix()
        assert dm.normal == {}
        assert dm.warning == {}
        assert dm.critical == {}
        assert dm.emergency == {}

    def test_custom(self):
        dm = DegradationMatrix(
            normal={"scheduler": "30s"},
            warning={"scheduler": "60s"},
            critical={"scheduler": "120s"},
            emergency={"scheduler": "paused"},
        )
        assert dm.normal["scheduler"] == "30s"
        assert dm.emergency["scheduler"] == "paused"
