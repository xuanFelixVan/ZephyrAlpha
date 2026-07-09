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

# NOTE: 本包仅保留 scope_guard 与 task_lifecycle_manager 两个活模块。
# resource_optimization_engine.py / lazy_loader.py 已删除（死代码，canonical 在
# zephyr.trading.resource_optimization 与 zephyr.shared.lifecycle.lazy_loader）。
# 历史遗留的 __all__ façade 条目（CacheStats/DaemonRegistry/PressureLevel 等）从未在此
# 导入，会引发 ImportError，已清除。
__all__ = ["scope_guard"]
