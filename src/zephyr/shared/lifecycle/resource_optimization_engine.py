# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §
# Re-export shim — canonical location is now zephyr.runtime.resource_optimization

from zephyr.runtime.resource_optimization import (
    CacheStats,
    CircuitBreaker,
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
    ResourceOptimizationEngine,
    ResourceSnapshot,
)

__all__ = [
    "CacheStats",
    "CircuitBreaker",
    "CircuitBreakerState",
    "DefensiveStrategy",
    "DegradationMatrix",
    "HealthCheckResult",
    "OptimizationRecord",
    "OptimizationResult",
    "OptimizationStrategy",
    "PressureLevel",
    "PressureState",
    "ProcessPoolStats",
    "ResourceOptimizationEngine",
    "ResourceSnapshot",
]
