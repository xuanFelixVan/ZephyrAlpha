# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §phase1-gate
# [MODULE] zephyr.governance.a2a
# [DOMAIN] D_GOVERNANCE
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# Phase 1 gate marker（a2a 为 trae_028 grandfathered 缩写目录，非 kebab-case）。Implementation in zephyr.infrastructure.a2a_protocol.

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: A2A 协议 Phase1 门禁标记字面量
#   fields: 阶段标记常量字符串 'a2a-v1'
#   code: src/zephyr/governance/a2a/__init__.py L8
# 层: 算法
# - id: A1
#   name_zh: ① 阶段门禁标记常量声明
#   name_en: A2A_PHASE1_MARKER
#   intro: 声明 a2a-v1 常量作为 A2A 协议 Phase1 门禁锚点（grandfathered 缩写目录占位）
#   desc: 模块级常量赋值；__all__ 为空列表不导出任何符号；真正实现位于 zephyr.infrastructure.a2a_protocol
#   inputs: I1
#   outputs: 阶段标记常量 'a2a-v1'
#   invariant: __all__ 恒为空列表
# 层: 输出
# - id: O1
#   name_zh: A2A Phase1 门禁标记常量
#   name_en: A2A_PHASE1_MARKER
#   intro: 供阶段门禁比对的标记常量，全仓仅本文件自引用
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

A2A_PHASE1_MARKER = "a2a-v1"

__all__: list[str] = []
