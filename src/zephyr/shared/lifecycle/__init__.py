# [A_module] module_id=MOD-SHR-lifecycle | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [TTL] permanent

# P7a (AI-15 audit 2026-07-16): removed dead code — _RO_LAZY_NAMES + __getattr__
# pointed to non-existent zephyr.integration.runtime_core.resource_optimization (0 consumers).
# canonical is zephyr.trading.resource_optimization.
# Also removed 3 ghost __all__ entries (*_from_infra) with no definition/import.
# AI-15 audit (2026-08-17): removed dangling __all__ entry "resource_optimization_engine" —
# 该 shim 文件已不存在（P7b/P7c 已退役），悬空条目导致 from-import 断链。

"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: __init__.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 daemon_registry, hooks, lazy_loader, resource_optimization_models（共 4 符号）
#   desc: __init__ import L0；__all__ 4 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（4 符号）
#   name_en: __all__
#   intro: daemon_registry, hooks, lazy_loader, resource_optimization_models
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = [
    "daemon_registry",
    "hooks",
    "lazy_loader",
    "resource_optimization_models",
]
# proxy shells removed (ARCH-DEBT 5.174 #6): scope_guard, task_lifecycle_manager
# import from zephyr.infrastructure.lifecycle.* directly
