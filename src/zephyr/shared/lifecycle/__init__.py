# [A_module] module_id=MOD-SHR_lifecycle | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [TTL] permanent

import importlib

_RO_LAZY_NAMES = {
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
}


def __getattr__(name: str):
    if name in _RO_LAZY_NAMES:
        _ro = importlib.import_module("zephyr.integration.runtime_core.resource_optimization")
        if name in _ro.__all__:
            return getattr(_ro, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "daemon_registry",
    "daemon_registry_from_infra",
    "hooks",
    "hooks_from_infra",
    "lazy_loader",
    "resource_optimization_engine",
    "resource_optimization_models",
    "resource_optimization_models_from_infra",
]
# proxy shells removed (ARCH-DEBT 5.174 #6): scope_guard, task_lifecycle_manager
# import from zephyr.infrastructure.lifecycle.* directly
