# [A_module] module_id=MOD-INF_lifecycle | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-107 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.infrastructure.lifecycle
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""core.lifecycle — lifecycle management, resource optimization, and module lifecycle hooks."""

from . import scope_guard

__all__ = [
    "CacheStats",
    "CircuitBreaker",
    "CircuitBreakerState",
    "ClampedPercent",
    "DaemonEntry",
    "DaemonPressureLevel",
    "DaemonRegistry",
    "DaemonResourceSnapshot",
    "DaemonState",
    "DefensiveStrategy",
    "DegradationMatrix",
    "HealthCheckResult",
    "LazyModuleRegistry",
    "LifecycleAware",
    "LifecycleManager",
    "LifecycleState",
    "ModuleEntry",
    "ModuleHealth",
    "OptimizationRecord",
    "OptimizationResult",
    "OptimizationStrategy",
    "PressureLevel",
    "PressureState",
    "ProcessPoolStats",
    "ResourceOptimizationEngine",
    "ResourceSnapshot",
    "daemon_registry",
    "hooks",
    "lazy_loader",
    "registry",
    "resource_optimization_engine",
    "resource_optimization_models",
    "scope_guard",
    "task_lifecycle_manager",
]
