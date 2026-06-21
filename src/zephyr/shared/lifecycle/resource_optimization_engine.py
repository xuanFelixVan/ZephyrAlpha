# [A_module] module_id=MOD-SHR_resource_optimization_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md | §
# Re-export shim — canonical location is now zephyr.trading.resource_optimization

import importlib

_RO_NAMES = {
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
    "_HysteresisConfig",
    "_PressureStateMachine",
    "_PressureThresholds",
}


def __getattr__(name):
    if name in _RO_NAMES:
        _mod = importlib.import_module("zephyr.trading.resource_optimization")
        _val = getattr(_mod, name)
        globals()[name] = _val
        return _val
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

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
    "_HysteresisConfig",
    "_PressureStateMachine",
    "_PressureThresholds",
]
