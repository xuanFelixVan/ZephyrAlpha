# [A_module] module_id=MOD-INF-hooks | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: HookRegistry, TransitionEvent, hook_registry
#   code: __init__.py import L34
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 HookRegistry, TransitionEvent, event_hook, hook_registry（共 4 符号）
#   desc: __init__ import L34；__all__ 4 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（4 符号）
#   name_en: __all__
#   intro: HookRegistry, TransitionEvent, event_hook, hook_registry
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.infrastructure.hooks.event_hook import HookRegistry, TransitionEvent, hook_registry

__all__ = ["HookRegistry", "TransitionEvent", "event_hook", "hook_registry"]
