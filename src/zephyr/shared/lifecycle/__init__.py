# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §

from .hooks import LifecycleAware, LifecycleManager, LifecycleState, ModuleHealth  # noqa: E402
from .daemon_registry import DaemonRegistry, DaemonState, registry  # noqa: E402

_RO_LAZY_NAMES = {
    "CacheStats", "CircuitBreaker", "CircuitBreakerState",
    "DefensiveStrategy", "DegradationMatrix", "HealthCheckResult",
    "OptimizationRecord", "OptimizationResult", "OptimizationStrategy",
    "PressureLevel", "PressureState", "ProcessPoolStats",
    "ResourceOptimizationEngine", "ResourceSnapshot",
}

def __getattr__(name: str):
    if name in _RO_LAZY_NAMES:
        from zephyr.runtime import resource_optimization as _ro
        if name in _ro.__all__:
            return getattr(_ro, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ['daemon_registry', 'hooks', 'lazy_loader', 'resource_optimization_engine', 'resource_optimization_models']
