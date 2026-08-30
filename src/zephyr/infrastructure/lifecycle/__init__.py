# [A_module] module_id=MOD-INF-lifecycle | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
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
"""
core.lifecycle — lifecycle management, resource optimization, and module lifecycle hooks.

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
#   intro: 再导出 scope_guard（共 1 符号）
#   desc: __init__ import L0；__all__ 1 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（1 符号）
#   name_en: __all__
#   intro: scope_guard
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from . import scope_guard

# NOTE: 本包仅保留 scope_guard 与 task_lifecycle_manager 两个活模块。
# resource_optimization_engine.py / lazy_loader.py 已删除（死代码，canonical 在
# zephyr.trading.resource_optimization 与 zephyr.shared.lifecycle.lazy_loader）。
# 历史遗留的 __all__ façade 条目（CacheStats/DaemonRegistry/PressureLevel 等）从未在此
# 导入，会引发 ImportError，已清除。
__all__ = ["scope_guard"]
