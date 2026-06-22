# [A_module] module_id=MOD-INT_lifecycle | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared_08.lifecycle
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]

from .daemon_registry import (
    DaemonEntry,
    DaemonRegistry,
    DaemonState,
    PressureLevel,
    ResourceSnapshot,
    registry,
)
from .hooks import (
    LifecycleAware,
    LifecycleManager,
    LifecycleState,
    ModuleHealth,
)
from .lazy_loader import (
    LazyModuleRegistry,
    ModuleEntry,
)

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
        import importlib

        _ro = importlib.import_module("zephyr.integration.runtime_core.resource_optimization")
        if name in _ro.__all__:
            return getattr(_ro, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "DaemonEntry",
    "DaemonRegistry",
    "DaemonState",
    "LazyModuleRegistry",
    "LifecycleAware",
    "LifecycleManager",
    "LifecycleState",
    "ModuleEntry",
    "ModuleHealth",
    "PressureLevel",
    "ResourceSnapshot",
    "daemon_registry",
    "hooks",
    "lazy_loader",
    "registry",
    "resource_optimization_engine",
    "resource_optimization_models",
]
