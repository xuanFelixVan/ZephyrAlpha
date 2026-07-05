# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.lifecycle.resource_optimization_models
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS] shared.io.io_cache; shared.infra.process_pool; runtime.resource_optimization; shared.lifecycle.resource_optimization_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_resource_optimization_models | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
models.py - Pydantic data models for resource optimization engine
=================================================================

SSoT: MOD-RESOURCE_OPTIMIZATION_ENGINE resource-optimization-engine/blueprint.md §3.2

Separated from resource_optimization_engine.py to avoid circular imports.
io_cache.py and streaming_reader.py import from here, not from the engine.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic.functional_validators import BeforeValidator


def _clamp_percent(v: float) -> float:
    return max(0.0, min(100.0, v))


ClampedPercent = Annotated[float, BeforeValidator(_clamp_percent), Field(ge=0.0, le=100.0)]


class PressureLevel(str, Enum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class OptimizationStrategy(str, Enum):
    CACHE_WARM = "cache_warm"
    IO_BATCH = "io_batch"
    PROCESS_POOL = "process_pool"
    LAZY_INIT = "lazy_init"
    STREAMING_READ = "streaming_read"
    SCHEDULE_ADAPT = "schedule_adapt"
    MEMORY_COMPACT = "memory_compact"


class DefensiveStrategy(str, Enum):
    STOP_LOW_PRIORITY = "stop_low_priority"
    RELEASE_MEMORY = "release_memory"
    REDUCE_FREQUENCY = "reduce_frequency"
    EMERGENCY_GC = "emergency_gc"


class CircuitBreakerState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class ResourceSnapshot(BaseModel):
    timestamp: float = Field(default_factory=lambda: __import__("time").time())
    cpu_percent: ClampedPercent = 0.0
    memory_percent: ClampedPercent = 0.0
    memory_used_gb: float = Field(default=0.0, ge=0.0)
    memory_total_gb: float = Field(default=0.0, ge=0.0)
    process_count: int = Field(default=0, ge=0)
    thread_count: int = Field(default=0, ge=0)
    disk_io_read_mb_s: float = Field(default=0.0, ge=0.0)
    disk_io_write_mb_s: float = Field(default=0.0, ge=0.0)
    disk_free_gb: float = Field(default=0.0, ge=0.0)
    pressure: PressureLevel = Field(default=PressureLevel.NORMAL)


class OptimizationRecord(BaseModel):
    timestamp: float = Field(default_factory=lambda: __import__("time").time())
    trigger: PressureLevel
    strategy: OptimizationStrategy
    actions_taken: list[str] = Field(default_factory=list)
    memory_before_gb: float = Field(default=0.0)
    memory_after_gb: float = Field(default=0.0)
    process_count_before: int = Field(default=0)
    process_count_after: int = Field(default=0)
    quality_preserved: bool = Field(default=True)
    duration_ms: int = Field(default=0, ge=0)
    success: bool = Field(default=True)


class OptimizationResult(BaseModel):
    strategy: OptimizationStrategy
    success: bool
    actions_taken: list[str] = Field(default_factory=list)
    snapshot_before: ResourceSnapshot
    snapshot_after: ResourceSnapshot | None = None
    quality_preserved: bool = Field(default=True)
    error_message: str | None = None


class CacheStats(BaseModel):
    total_entries: int = Field(default=0, ge=0)
    hit_count: int = Field(default=0, ge=0)
    miss_count: int = Field(default=0, ge=0)
    hit_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    memory_usage_mb: float = Field(default=0.0, ge=0.0)
    evictions: int = Field(default=0, ge=0)


class ProcessPoolStats(BaseModel):
    active_processes: int = Field(default=0, ge=0)
    max_processes: int = Field(default=30, ge=1)
    reuse_count: int = Field(default=0, ge=0)
    zombie_count: int = Field(default=0, ge=0)
    idle_count: int = Field(default=0, ge=0)


class PressureState(BaseModel):
    current_level: PressureLevel = Field(default=PressureLevel.NORMAL)
    previous_level: PressureLevel | None = None
    entered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    transition_count: int = Field(default=0, ge=0)
    cooldown_remaining_s: float = Field(default=0.0, ge=0.0)


class HealthCheckResult(BaseModel):
    engine_running: bool
    monitor_loop_alive: bool
    last_snapshot_age_s: float = Field(default=0.0, ge=0.0)
    pressure_level: PressureLevel = Field(default=PressureLevel.NORMAL)
    daemon_count: int = Field(default=0, ge=0)
    cache_healthy: bool = Field(default=True)
    process_pool_healthy: bool = Field(default=True)


class DegradationMatrix(BaseModel):
    normal: dict[str, str] = Field(default_factory=dict)
    warning: dict[str, str] = Field(default_factory=dict)
    critical: dict[str, str] = Field(default_factory=dict)
    emergency: dict[str, str] = Field(default_factory=dict)
