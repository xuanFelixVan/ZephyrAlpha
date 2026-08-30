# [A_module] module_id=MOD-SHR-core | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §
# [TTL] permanent
"""
shared.contracts.core — auto-generated package init.

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
#   intro: 再导出 base_event, enforcer, factories, gate_types, registry, runtime_plane_tag, s…
#   desc: __init__ import L0；__all__ 9 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（9 符号）
#   name_en: __all__
#   intro: base_event, enforcer, factories, gate_types, registry, runtime_plane_tag, syste…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from . import base_event, gate_types

__all__ = [
    "base_event",
    "enforcer",
    "factories",
    "gate_types",
    "registry",
    "runtime_plane_tag",
    "system_configuration",
    "timestamp",
    "trace_context",
]
