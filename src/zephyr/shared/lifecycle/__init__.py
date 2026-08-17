# [A_module] module_id=MOD-SHR-lifecycle | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [TTL] permanent

# P7a (AI-15 audit 2026-07-16): removed dead code — _RO_LAZY_NAMES + __getattr__
# pointed to non-existent zephyr.integration.runtime_core.resource_optimization (0 consumers).
# canonical is zephyr.trading.resource_optimization.
# Also removed 3 ghost __all__ entries (*_from_infra) with no definition/import.
# AI-15 audit (2026-08-17): removed dangling __all__ entry "resource_optimization_engine" —
# 该 shim 文件已不存在（P7b/P7c 已退役），悬空条目导致 from-import 断链。

__all__ = [
    "daemon_registry",
    "hooks",
    "lazy_loader",
    "resource_optimization_models",
]
# proxy shells removed (ARCH-DEBT 5.174 #6): scope_guard, task_lifecycle_manager
# import from zephyr.infrastructure.lifecycle.* directly
