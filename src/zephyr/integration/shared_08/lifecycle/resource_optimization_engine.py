# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared_08.lifecycle.resource_optimization_engine
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INT_resource_optimization_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# Re-export shim — canonical location is now zephyr.trading.resource_optimization

import importlib as _importlib

_mod = _importlib.import_module("zephyr.trading.resource_optimization")
CacheStats = _mod.CacheStats
CircuitBreaker = _mod.CircuitBreaker
CircuitBreakerState = _mod.CircuitBreakerState
DefensiveStrategy = _mod.DefensiveStrategy
DegradationMatrix = _mod.DegradationMatrix
HealthCheckResult = _mod.HealthCheckResult
OptimizationRecord = _mod.OptimizationRecord
OptimizationResult = _mod.OptimizationResult
OptimizationStrategy = _mod.OptimizationStrategy
PressureLevel = _mod.PressureLevel
PressureState = _mod.PressureState
ProcessPoolStats = _mod.ProcessPoolStats
ResourceOptimizationEngine = _mod.ResourceOptimizationEngine
ResourceSnapshot = _mod.ResourceSnapshot

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
