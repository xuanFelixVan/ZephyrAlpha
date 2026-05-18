# [BLUEPRINT] MOD-INF-002 | 03_modules/l01_infrastructure/runtime-integration/blueprint.md | §
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md | §
"""core.lifecycle — lifecycle management, resource optimization, and module lifecycle hooks."""

from .hooks import LifecycleAware, LifecycleManager, LifecycleState, ModuleHealth
from .daemon_registry import DaemonEntry, DaemonRegistry, DaemonState, PressureLevel as DaemonPressureLevel, ResourceSnapshot as DaemonResourceSnapshot, registry
from .lazy_loader import LazyModuleRegistry, ModuleEntry
from .resource_optimization_models import (
    CacheStats,
    CircuitBreakerState,
    ClampedPercent,
    DefensiveStrategy,
    DegradationMatrix,
    HealthCheckResult,
    OptimizationRecord,
    OptimizationResult,
    OptimizationStrategy,
    PressureLevel,
    ProcessPoolStats,
    ResourceSnapshot,
    PressureState,
)
from .resource_optimization_engine import (
    CircuitBreaker,
    ResourceOptimizationEngine,
)
from . import scope_guard

__all__ = [
    'scope_guard',
    'task_lifecycle_manager',
    'hooks',
    'lazy_loader',
    'registry',
    'resource_optimization_models',
    'CacheStats',
    'CircuitBreaker',
    'CircuitBreakerState',
    'ClampedPercent',
    'DaemonEntry',
    'DaemonPressureLevel',
    'DaemonRegistry',
    'DaemonResourceSnapshot',
    'DaemonState',
    'DefensiveStrategy',
    'DegradationMatrix',
    'HealthCheckResult',
    'LazyModuleRegistry',
    'LifecycleAware',
    'LifecycleManager',
    'LifecycleState',
    'ModuleEntry',
    'ModuleHealth',
    'OptimizationRecord',
    'OptimizationResult',
    'OptimizationStrategy',
    'PressureLevel',
    'PressureState',
    'ProcessPoolStats',
    'ResourceOptimizationEngine',
    'ResourceSnapshot',
    'daemon_registry',
    'resource_optimization_engine',
]
